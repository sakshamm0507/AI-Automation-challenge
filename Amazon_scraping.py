import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time

# Define headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

# Function to scrape data from a single page
def scrape_amazon_page(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    products = []
    
    # Find all product containers
    product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})
    
    for product in product_containers:
        # Check if it's a sponsored product
        sponsored_tag = product.find('span', text=lambda t: t and 'Sponsored' in t)
        if not sponsored_tag:
            continue
        
        # Extract product details
        title_element = product.find('h2')
        title = title_element.text.strip() if title_element else "N/A"
        
        brand_element = product.find('span', {'class': 'a-size-base-plus'})
        brand = brand_element.text.strip() if brand_element else "Unknown"
        
        rating_element = product.find('span', {'class': 'a-icon-alt'})
        rating = rating_element.text.split(' ')[0] if rating_element else "0"
        
        reviews_element = product.find('span', {'class': 'a-size-base s-underline-text'})
        reviews = reviews_element.text.strip().replace(',', '') if reviews_element else "0"
        
        price_element = product.find('span', {'class': 'a-price-whole'})
        price = price_element.text.strip().replace(',', '') if price_element else "0"
        
        img_element = product.find('img', {'class': 's-image'})
        img_url = img_element['src'] if img_element else "N/A"
        
        url_element = product.find('a', {'class': 'a-link-normal s-no-outline'})
        product_url = "https://www.amazon.in" + url_element['href'] if url_element else "N/A"
        
        # Add to products list
        products.append({
            'Title': title,
            'Brand': brand,
            'Rating': rating,
            'Reviews': reviews,
            'Price': price,
            'Image URL': img_url,
            'Product URL': product_url
        })
    
    return products

# Function to scrape multiple pages
def scrape_amazon(keyword, pages=5):
    all_products = []
    base_url = f"https://www.amazon.in/s?k={keyword.replace(' ', '+')}"
    
    for page in range(1, pages + 1):
        print(f"Scraping page {page}...")
        page_url = f"{base_url}&page={page}"
        products_on_page = scrape_amazon_page(page_url)
        all_products.extend(products_on_page)
        
        # Add delay between requests to avoid getting blocked
        time.sleep(2)
    
    return all_products

# Function to clean and prepare data
def clean_data(data):
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Remove duplicates based on the "Title" column
    df.drop_duplicates(subset=['Title'], inplace=True)
    
    # Convert columns to appropriate data types
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')
    
    # Drop rows with missing or invalid values in critical columns
    df.dropna(subset=['Price', 'Rating', 'Reviews'], inplace=True)
    
    # Reset index after cleaning
    df.reset_index(drop=True, inplace=True)
    
    return df

# Function to analyze data
def analyze_data(df):
    # Brand Performance Analysis
    print("\nPerforming Brand Performance Analysis...")
    
    # Brand Frequency
    brand_counts = df['Brand'].value_counts().head(5)
    print("\nTop 5 Brands by Frequency:")
    print(brand_counts)
    
    # Average Rating by Brand
    avg_rating_by_brand = df.groupby('Brand')['Rating'].mean().sort_values(ascending=False).head(5)
    print("\nTop 5 Brands by Average Rating:")
    print(avg_rating_by_brand)
    
    # Visualization: Top 5 Brands by Frequency
    plt.figure(figsize=(10, 6))
    sns.barplot(x=brand_counts.values, y=brand_counts.index, palette='viridis')
    plt.title("Top 5 Brands by Frequency")
    plt.xlabel("Frequency")
    plt.ylabel("Brand")
    plt.tight_layout()
    plt.savefig("top_5_brands_by_frequency.png")
    plt.show()
    
    # Visualization: Percentage Share of Top Brands
    plt.figure(figsize=(8, 8))
    brand_counts.plot.pie(autopct='%1.1f%%', startangle=90, colors=sns.color_palette('viridis', len(brand_counts)))
    plt.title("Percentage Share of Top 5 Brands")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig("percentage_share_top_brands.png")
    plt.show()

    # Price vs. Rating Analysis
    print("\nPerforming Price vs. Rating Analysis...")
    
    # Scatter Plot: Price vs. Rating
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Price', y='Rating', data=df, alpha=0.7, color='blue')
    plt.title("Price vs. Rating")
    plt.xlabel("Price (₹)")
    plt.ylabel("Rating")
    plt.tight_layout()
    plt.savefig("price_vs_rating_scatter.png")
    plt.show()
    
    # Average Price by Rating Range
    df['Rating Range'] = pd.cut(df['Rating'], bins=[0, 2, 3, 4, 5], labels=['0-2', '2-3', '3-4', '4-5'])
    avg_price_by_rating = df.groupby('Rating Range')['Price'].mean()
    print("\nAverage Price by Rating Range:")
    print(avg_price_by_rating)
    
    # Bar Chart: Average Price by Rating Range
    plt.figure(figsize=(10, 6))
    sns.barplot(x=avg_price_by_rating.index, y=avg_price_by_rating.values, palette='coolwarm')
    plt.title("Average Price by Rating Range")
    plt.xlabel("Rating Range")
    plt.ylabel("Average Price (₹)")
    plt.tight_layout()
    plt.savefig("average_price_by_rating_range.png")
    plt.show()

    # Review & Rating Distribution
    print("\nPerforming Review & Rating Distribution Analysis...")
    
    # Top 5 Products by Reviews
    top_reviewed = df.nlargest(5, 'Reviews')[['Title', 'Reviews']]
    print("\nTop 5 Products by Reviews:")
    print(top_reviewed)
    
    # Bar Chart: Top 5 Products by Reviews
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Reviews', y='Title', data=top_reviewed, palette='magma')
    plt.title("Top 5 Products by Reviews")
    plt.xlabel("Number of Reviews")
    plt.ylabel("Product Title")
    plt.tight_layout()
    plt.savefig("top_5_products_by_reviews.png")
    plt.show()
    
    # Top 5 Products by Rating
    top_rated = df.nlargest(5, 'Rating')[['Title', 'Rating']]
    print("\nTop 5 Products by Rating:")
    print(top_rated)
    
    # Bar Chart: Top 5 Products by Rating
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Rating', y='Title', data=top_rated, palette='plasma')
    plt.title("Top 5 Products by Rating")
    plt.xlabel("Rating")
    plt.ylabel("Product Title")
    plt.tight_layout()
    plt.savefig("top_5_products_by_rating.png")
    plt.show()

if __name__ == "__main__":
    # Let the user input the search query
    search_query = input("Enter the search query: ")
    pages_to_scrape = int(input("Enter the number of pages to scrape: "))
    
    # Scrape data for the user-provided query
    scraped_data = scrape_amazon(search_query, pages=pages_to_scrape)
    
    # Clean and prepare the scraped data
    cleaned_data = clean_data(scraped_data)
    
    # Save the cleaned data to a CSV file
    output_file = f"amazon_{search_query.replace(' ', '_')}_cleaned.csv"
    cleaned_data.to_csv(output_file, index=False)
    print(f"Scraping and cleaning completed! Data saved to {output_file}.")
    
    # Perform analysis
    analyze_data(cleaned_data)
