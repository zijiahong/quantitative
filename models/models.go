package models

type Quote struct {
	Timestamp    float64 `json:"timestamp"`
	Volume       float64 `json:"volume"`
	Open         float64 `json:"open"`
	High         float64 `json:"high"`
	Low          float64 `json:"low"`
	Close        float64 `json:"close"`
	Chg          float64 `json:"chg"`
	Percent      float64 `json:"percent"`
	TurnoverRate float64 `json:"turnoverrate"`
	Amount       float64 `json:"amount"`
	Dea          float64 `json:"dea"`
	Dif          float64 `json:"dif"`
	Macd         float64 `json:"macd"`
}
