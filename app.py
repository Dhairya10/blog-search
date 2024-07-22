import streamlit as st
from typesense_search import TypesenseSearch

def main():
    st.set_page_config(page_title="Blog Search", page_icon="🔍")

    st.title("Blog Search")

    # Load external CSS
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # User input
    query = st.text_input("Enter your search query")

    # Author selection
    typesense_search = TypesenseSearch()
    authors = ["all", "jason", "dhh"]
    selected_author = st.selectbox("Select an author", authors)

    # Number of results selection
    num_results = st.slider("Number of results", min_value=1, max_value=10, value=3, step=1)

    if st.button("Search"):
        if query:
            # Pass selected author to search function if not "all"
            author = selected_author if selected_author != "all" else None
            results = typesense_search.search(query, author=author, limit=num_results)
            
            if results:
                st.subheader(f"Search Results for '{query}'")
                for result in results:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-title">{result['title']}</div>
                        <div class="result-author">Author - {result['author']}</div>
                        <div class="result-url"><a href="{result['url']}" target="_blank">{result['url']}</a></div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No results found.")
        else:
            st.warning("Please enter a search query.")

if __name__ == "__main__":
    main()