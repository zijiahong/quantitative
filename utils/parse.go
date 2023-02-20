package utils

import (
	"encoding/json"

	"github.com/zijiahong/quantitative/models"
)

type Data struct {
	Symbol string          `json:"symbol"`
	Column []string        `json:"column"`
	Item   [][]interface{} `json:"item"`
}

// 假设上面的 StockData 结构体已经定义

func ParseStockData(data []byte) ([]models.Quote, error) {

	var dataWrapper struct {
		Data Data `json:"data"`
	}

	err := json.Unmarshal(data, &dataWrapper)
	if err != nil {
		return nil, err
	}

	quotes := make([]models.Quote, 0, len(dataWrapper.Data.Item))
	for _, item := range dataWrapper.Data.Item {
		quote := models.Quote{
			Timestamp:    item[0].(float64),
			Volume:       item[1].(float64),
			Open:         item[2].(float64),
			High:         item[3].(float64),
			Low:          item[4].(float64),
			Close:        item[5].(float64),
			Chg:          item[6].(float64),
			Percent:      item[7].(float64),
			TurnoverRate: item[8].(float64),
			Amount:       item[9].(float64),
		}
		quotes = append(quotes, quote)
	}

	return quotes, nil
}
