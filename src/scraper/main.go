package main

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"golang.org/x/net/html"
	"golang.org/x/net/proxy"
)

type Result struct {
	URL    string   `json:"url"`
	Status string   `json:"status"`
	Links  []string `json:"links"`
	HTML   string   `json:"html"`
}

var torClient *http.Client

func newTorClient(socksAddr string, timeout time.Duration) (*http.Client, error) {
	dialer, err := proxy.SOCKS5("tcp", socksAddr, nil, proxy.Direct)
	if err != nil {
		return nil, err
	}
	dialContext := func(ctx context.Context, network, addr string) (net.Conn, error) {
		return dialer.Dial(network, addr)
	}
	tr := &http.Transport{
		DialContext:         dialContext,
		ForceAttemptHTTP2:   false,
		DisableKeepAlives:   false,
		MaxIdleConns:        10,
		IdleConnTimeout:     90 * time.Second,
		TLSHandshakeTimeout: 10 * time.Second,
	}
	client := &http.Client{
		Transport: tr,
		Timeout:   timeout,
	}
	return client, nil
}

func fetch(url string) (*http.Response, error) {
	if torClient != nil {
		return torClient.Get(url)
	}
	return http.Get(url)
}

func extractLinksFromReader(r io.Reader) ([]string, error) {
	links := []string{}
	doc, err := html.Parse(r)
	if err != nil {
		return links, err
	}
	var f func(*html.Node)
	f = func(n *html.Node) {
		if n.Type == html.ElementNode && n.Data == "a" {
			for _, attr := range n.Attr {
				if attr.Key == "href" && strings.HasPrefix(attr.Val, "http") {
					links = append(links, attr.Val)
				}
			}
		}
		for c := n.FirstChild; c != nil; c = c.NextSibling {
			f(c)
		}
	}
	f(doc)
	return links, nil
}

func scrapeURL(url string, results chan<- Result, wg *sync.WaitGroup) {
	defer wg.Done()
	resp, err := fetch(url)
	if err != nil {
		results <- Result{URL: url, Status: "Error: " + err.Error(), Links: []string{}, HTML: ""}
		return
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		results <- Result{URL: url, Status: "Error reading body: " + err.Error(), Links: []string{}, HTML: ""}
		return
	}
	links, _ := extractLinksFromReader(strings.NewReader(string(body)))
	result := Result{URL: url, Status: resp.Status, Links: links, HTML: string(body)}
	results <- result
}

func main() {
	var err error
	torClient, err = newTorClient("127.0.0.1:9050", 60*time.Second)
	if err != nil {
		log.Fatalf("failed to create tor client: %v", err)
	}
	file, err := os.Open("url.txt")
	if err != nil {
		log.Fatal("Error opening url.txt:", err)
	}
	defer file.Close()
	var urls []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		url := strings.TrimSpace(scanner.Text())
		if url != "" {
			urls = append(urls, url)
		}
	}
	if err := scanner.Err(); err != nil {
		log.Fatal("Error reading url.txt:", err)
	}
	if len(urls) == 0 {
		log.Fatal("No URLs found in url.txt")
	}
	var wg sync.WaitGroup
	results := make(chan Result, len(urls))
	for _, url := range urls {
		wg.Add(1)
		go scrapeURL(url, results, &wg)
	}
	go func() {
		wg.Wait()
		close(results)
	}()
	var allResults []Result
	for result := range results {
		allResults = append(allResults, result)
		fmt.Printf("Completed scraping: %s\n", result.URL)
	}
	f, err := os.Create("data.json")
	if err != nil {
		log.Fatal("Create data.json error:", err)
	}
	defer f.Close()
	enc := json.NewEncoder(f)
	enc.SetEscapeHTML(false)
	enc.SetIndent("", "  ")
	if err := enc.Encode(allResults); err != nil {
		log.Fatal("JSON encode error:", err)
	}
	fmt.Printf("Successfully scraped %d URLs\n", len(allResults))
}

