# NewsDigest

NewsDigest is an AI-powered news summarization application that generates concise and insightful summaries of news articles based on a user-provided topic. It leverages the OpenAI API to analyze and synthesize the news content, providing users with a quick overview of the latest news on their topics of interest.

## Features

- Enter a topic of interest to retrieve relevant news articles
- Utilizes the NewsAPI to fetch the latest news articles
- Generates well-organized summaries for each article, including the title, author, source, and a brief synopsis
- Provides a sentiment analysis of the overall news coverage, indicating the prevailing sentiment (positive, negative, or neutral)
- User-friendly interface powered by Streamlit for easy interaction

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/rebornify/newsdigest.git
   ```

2. Navigate to the project directory:
   ```
   cd newsdigest
   ```

3. Create a virtual environment (optional but recommended):
   ```
   python -m venv .venv
   ```

4. Activate the virtual environment:
   - For Windows:
     ```
     .venv\Scripts\activate
     ```
   - For macOS and Linux:
     ```
     source .venv/bin/activate
     ```

5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

6. Set up the required API keys:
   - Create a `.env` file in the project root directory
   - Add your OpenAI API key and NewsAPI key in the following format:
     ```
     OPENAI_API_KEY=your-openai-api-key
     NEWS_API_KEY=your-newsapi-key
     ```

## Usage

1. Make sure you have activated the virtual environment (if you created one)

2. Run the application:
   ```
   streamlit run main.py
   ```

3. Access the application in your web browser at `http://localhost:8501`

4. Enter a topic of interest in the input field and click the "Run Assistant" button

5. The application will fetch relevant news articles, generate summaries, and provide a sentiment analysis

6. Read through the summaries and sentiment analysis to quickly grasp the key points and overall narrative of the news coverage

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## Contact

If you have any questions or inquiries, feel free to reach out to me at [oyscaleb@gmail.com](mailto:oyscaleb@gmail.com).