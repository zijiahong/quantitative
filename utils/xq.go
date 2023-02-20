package utils

import (
	"bytes"
	"fmt"
	"net/http"
	"net/url"
	"regexp"
)

func LoginXQ(username, password string) (string, error) {
	data := url.Values{}
	data.Set("username", username)
	data.Set("password", password)

	// 发送 POST 请求
	client := &http.Client{}
	req, err := http.NewRequest("POST", "https://xueqiu.com/user/login", bytes.NewBufferString(data.Encode()))
	if err != nil {
		return "", fmt.Errorf("创建请求失败: %v", err)
	}

	// 设置请求头
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
	req.Header.Set("Referer", "https://xueqiu.com/")

	// 发送请求
	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("请求失败: %v", err)
	}
	defer resp.Body.Close()

	// 从响应中解析出 xq_a_token
	regex := regexp.MustCompile(`xq_a_token=(\w+);`)
	match := regex.FindStringSubmatch(resp.Header.Get("Set-Cookie"))
	if len(match) < 2 {
		return "", fmt.Errorf("解析 token 失败")
	}

	return match[1], nil
}
