package main

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"cloud.google.com/go/vertexai/genai"
	"google.golang.org/api/option"
)

// Response struct matches the required JSON schema
type Response struct {
	Response     string `json:"response"`
	Intent       string `json:"intent"`
	Request      string `json:"request"`
	TextLanguage string `json:"text_language"`
}

// ProjectInfo extracted from service account key
type ProjectInfo struct {
	ProjectID string `json:"project_id"`
}

func main() {
	// Path to service account key file
	keyFilePath := "key.json"

	// Path to local video file - using the correct path
	videoPath := filepath.Join("video", "video.mp4")

	// Get project ID from the key file
	projectID, err := getProjectID(keyFilePath)
	if err != nil {
		fmt.Printf("Error getting project ID: %v\n", err)
		os.Exit(1)
	}

	// Get user input
	fmt.Println("Masukkan pertanyaan Anda tentang video (atau tekan Enter untuk analisis default):")
	reader := bufio.NewReader(os.Stdin)
	userQuestion, _ := reader.ReadString('\n')
	userQuestion = strings.TrimSpace(userQuestion)

	// Determine the intent based on user question
	intent := determineIntent(userQuestion)

	// Process with Vertex AI
	result, err := analyzeVideoWithVertexAI(videoPath, projectID, keyFilePath, userQuestion, intent)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		os.Exit(1)
	}

	// Output JSON response
	jsonOutput, _ := json.MarshalIndent(result, "", "  ")
	fmt.Println(string(jsonOutput))
}

// Determine intent based on user question
func determineIntent(question string) string {
	question = strings.ToLower(question)

	if question == "" {
		return "OBJECT_DETECTION" // Default intent
	} else if strings.Contains(question, "makanan") || strings.Contains(question, "makan") || strings.Contains(question, "kuliner") {
		return "FOOD_QUESTION"
	} else if strings.Contains(question, "objek") || strings.Contains(question, "benda") || strings.Contains(question, "apa itu") {
		return "OBJECT_DETECTION"
	} else if strings.Contains(question, "tempat") || strings.Contains(question, "lokasi") || strings.Contains(question, "wisata") {
		return "POI_QUESTION"
	} else if strings.Contains(question, "budaya") || strings.Contains(question, "tradisi") || strings.Contains(question, "adat") {
		return "CULTURE_QUESTION"
	} else if strings.Contains(question, "terjemah") || strings.Contains(question, "translate") || strings.Contains(question, "arti") {
		return "TRANSLATION"
	} else {
		return "OTHERS"
	}
}

// Extract project ID from service account key file
func getProjectID(keyFilePath string) (string, error) {
	data, err := os.ReadFile(keyFilePath)
	if err != nil {
		return "", fmt.Errorf("failed to read key file: %v", err)
	}

	var projectInfo ProjectInfo
	err = json.Unmarshal(data, &projectInfo)
	if err != nil {
		return "", fmt.Errorf("failed to parse key file: %v", err)
	}

	return projectInfo.ProjectID, nil
}

// Read video file as bytes
func readVideoFile(path string) ([]byte, error) {
	// Check if file exists
	if _, err := os.Stat(path); os.IsNotExist(err) {
		// If not found, try to construct absolute path for debugging
		absPath, _ := filepath.Abs(path)
		return nil, fmt.Errorf("video file not found at path: %s (absolute: %s)", path, absPath)
	}

	return os.ReadFile(path)
}

func analyzeVideoWithVertexAI(videoPath, projectID, keyFilePath, userQuestion, intent string) (Response, error) {
	// Create context
	ctx := context.Background()

	// Location for Vertex AI - using a common default
	location := "us-central1"

	// Initialize Vertex AI client with service account key
	client, err := genai.NewClient(ctx, projectID, location, option.WithCredentialsFile(keyFilePath))
	if err != nil {
		return Response{}, err
	}
	defer client.Close()

	// Initialize Gemini model
	model := client.GenerativeModel("gemini-2.0-flash")

	// Read video file
	videoBytes, err := readVideoFile(videoPath)
	if err != nil {
		return Response{}, err
	}

	// Create instruction text part
	var instruction string
	if userQuestion == "" {
		instruction = "Kamu adalah Travel Buddy AI dari Telkomsel. Analisis konten video ini dan identifikasi apa yang ditampilkan. Jawab dalam Bahasa Indonesia."
	} else {
		instruction = fmt.Sprintf("Kamu adalah Travel Buddy AI dari Telkomsel. Pertanyaan: %s\nAnalisis video ini dan berikan jawaban yang sesuai dengan pertanyaan. Jawab dalam Bahasa Indonesia.", userQuestion)
	}

	textInstruction := genai.Text(instruction)

	// Create video blob part
	videoBlob := &genai.Blob{
		MIMEType: "video/mp4",
		Data:     videoBytes,
	}

	// Generate content passing the parts directly
	resp, err := model.GenerateContent(ctx, textInstruction, videoBlob)
	if err != nil {
		return Response{}, err
	}

	// Extract text from response
	var responseText string
	if len(resp.Candidates) > 0 && len(resp.Candidates[0].Content.Parts) > 0 {
		// Get the text from the response
		responseText = fmt.Sprintf("%v", resp.Candidates[0].Content.Parts[0])
	} else {
		return Response{}, fmt.Errorf("empty response from Vertex AI")
	}

	// Create structured response
	return Response{
		Response:     responseText,
		Intent:       intent,
		Request:      userQuestion,
		TextLanguage: "id",
	}, nil
}
