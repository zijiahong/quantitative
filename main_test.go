package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"testing"
	"time"
)

type StockData struct {
	LastClose float64 `json:"last_close"`
	After     []interface{}
	Items     []struct {
		Current   float64 `json:"current"`
		Volume    float64 `json:"volume"`
		AvgPrice  float64 `json:"avg_price"`
		Chg       float64 `json:"chg"`
		Percent   float64 `json:"percent"`
		Timestamp float64 `json:"timestamp"`
		Amount    float64 `json:"amount"`
		High      float64 `json:"high"`
		Low       float64 `json:"low"`
		MACD      struct {
			DIF  float64 `json:"dif"`
			DEA  float64 `json:"dea"`
			MACD float64 `json:"macd"`
		} `json:"macd"`
		KDJ           interface{} `json:"kdj"`
		Ratio         interface{} `json:"ratio"`
		Capital       interface{} `json:"capital"`
		VolumeCompare struct {
			VolumeSum     float64 `json:"volume_sum"`
			VolumeSumLast float64 `json:"volume_sum_last"`
		} `json:"volume_compare"`
	}
}

func TestMain(t *testing.T) {
	// 登录获取 token
	token := "a864e001a14fc0a58dcd23f087d80caf4e50ee1e"

	// 创建请求
	client := &http.Client{}
	req, err := http.NewRequest("GET", "https://stock.xueqiu.com/v5/stock/chart/minute.json?symbol=SH513050&period=1d&type=before&count=-1440&indicator=macd", nil)
	if err != nil {
		fmt.Println("创建请求失败:", err)
		return
	}

	// 设置请求头
	req.Header.Set("Cookie", fmt.Sprintf("xq_a_token=%s", token))
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")

	// 发送请求
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("请求失败:", err)
		return
	}
	defer resp.Body.Close()

	// 读取响应数据
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("读取数据失败:", err)
		return
	}

	// 解析响应数据
	var result struct {
		Data StockData `json:"data"`
	}
	err = json.Unmarshal(body, &result)
	if err != nil {
		fmt.Println("解析数据失败:", err)
		return
	}

	// 输出分时数据
	for _, item := range result.Data.Items {
		fmt.Printf("时间: %s, MACD: %f, DIF: %f, DEA: %f\n", time.Unix(int64(item.Timestamp)/1000, 0).Format("2006-01-02 15:04:05"), item.MACD.MACD, item.MACD.DIF, item.MACD.DEA)
	}
}
