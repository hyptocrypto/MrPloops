package main

import (
	"image/jpeg"
	"log"
	"net/http"

	"gocv.io/x/gocv"
)

func main() {
	webcam, err := gocv.OpenVideoCapture(0)
	if err != nil {
		log.Fatalf("Error opening capture device: %v", err)
	}
	defer webcam.Close()

	window := gocv.NewWindow("Webcam")
	defer window.Close()

	img := gocv.NewMat()
	defer img.Close()

	http.HandleFunc("/stream", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "multipart/x-mixed-replace; boundary=frame")

		for {
			if ok := webcam.Read(&img); !ok {
				log.Printf("Error reading frame from webcam")
				break
			}

			_, err := jpeg.Encode(w, img.ToImage(), nil)
			if err != nil {
				log.Printf("Error encoding frame: %v", err)
				break
			}
		}
	})

	log.Println("Starting server on port 4444...")
	log.Fatal(http.ListenAndServe(":4444", nil))
}
