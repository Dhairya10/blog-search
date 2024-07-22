# Blog Search

A simple web application built with Streamlit that allows users to search for blog posts using Typesense.

## Features

- Search for blog posts using keywords
- Filter results by author
- Adjust the number of search results displayed
- Responsive design with custom CSS styling

## Requirements

- Python 3.7+
- Streamlit
- Typesense

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/blog-search.git
   cd blog-search
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Typesense server and configure the connection details in `typesense_search.py`.

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Enter a search query, select an author (optional), and adjust the number of results to display.

4. Click the "Search" button to see the results.

## Project Structure

- `app.py`: Main Streamlit application file
- `typesense_search.py`: Contains the TypesenseSearch class for interacting with the Typesense server
- `style.css`: Custom CSS styles for the application