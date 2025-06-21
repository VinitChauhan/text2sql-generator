import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time

# Configuration
FASTAPI_URL = "http://fastapi:8000"  # Docker internal network

# Page configuration
st.set_page_config(
    page_title="Text2SQL Generator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    .sql-box {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 5px;
        padding: 15px;
        font-family: 'Courier New', monospace;
        margin: 10px 0;
    }
    .feedback-buttons {
        display: flex;
        gap: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def make_api_request(endpoint, method="GET", data=None):
    """Make API request to FastAPI backend"""
    try:
        url = f"{FASTAPI_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return None, f"Connection Error: {str(e)}"

def display_sql_query(sql_query, query_id=None):
    """Display SQL query in a formatted box"""
    st.markdown(f"""
    <div class="sql-box">
        <strong>Generated SQL Query:</strong><br>
        <code>{sql_query}</code>
    </div>
    """, unsafe_allow_html=True)

# Initialize session state
if 'current_query' not in st.session_state:
    st.session_state.current_query = None
if 'query_results' not in st.session_state:
    st.session_state.query_results = None
if 'feedback_submitted' not in st.session_state:
    st.session_state.feedback_submitted = False

# Main title
st.title("🔍 Text2SQL Generator")
st.markdown("Convert natural language to SQL queries with AI assistance")

# Sidebar
with st.sidebar:
    st.header("🛠️ System Status")
    
    # Health check
    health_data, health_error = make_api_request("/health")
    if health_data:
        st.success("✅ System Online")
        st.json(health_data)
    else:
        st.error("❌ System Offline")
        st.error(health_error)
    
    st.header("📊 Statistics")
    stats_data, stats_error = make_api_request("/feedback-stats")
    if stats_data:
        if stats_data.get('statistics'):
            for stat in stats_data['statistics']:
                emoji = "👍" if stat['feedback'] == 'thumbs_up' else "👎"
                st.metric(
                    f"{emoji} {stat['feedback'].replace('_', ' ').title()}", 
                    f"{stat['count']} ({stat['percentage']:.1f}%)"
                )

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Query Generator", "🗃️ Database Schema", "📈 Analytics", "⚙️ Settings"])

with tab1:
    st.header("Generate SQL from Natural Language")
    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_query = st.text_area(
            "Enter your question in natural language:",
            placeholder="e.g., Show me all customers who made orders in the last 30 days",
            height=100
        )
    
    with col2:
        st.markdown("### Examples:")
        st.markdown("""
        - List all products with price > 100
        - Count orders by month
        - Find top 5 customers by revenue
        - Show employees in Sales department
        """)
    
    # Generate button
    if st.button("🚀 Generate SQL", type="primary", use_container_width=True):
        if user_query.strip():
            with st.spinner("Generating SQL query..."):
                query_data, query_error = make_api_request(
                    "/generate-sql", 
                    "POST", 
                    {"text": user_query}
                )
                
                if query_data:
                    st.session_state.current_query = query_data
                    st.session_state.feedback_submitted = False
                    st.rerun()
                else:
                    st.error(f"Failed to generate SQL: {query_error}")
        else:
            st.warning("Please enter a question first!")
    
    # Display generated query
    if st.session_state.current_query:
        st.markdown("---")
        st.subheader("Generated SQL Query")
        
        query_data = st.session_state.current_query
        display_sql_query(query_data['generated_sql'])
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("▶️ Execute Query", type="secondary"):
                with st.spinner("Executing query..."):
                    exec_data, exec_error = make_api_request(
                        "/execute-sql",
                        "POST",
                        {"query": query_data['generated_sql']}
                    )
                    
                    if exec_data:
                        st.session_state.query_results = exec_data
                        st.rerun()
                    else:
                        st.error(f"Query execution failed: {exec_error}")
        
        with col2:
            if st.button("📋 Copy Query"):
                st.code(query_data['generated_sql'], language='sql')
                st.success("Query copied to clipboard!")
        
        # Feedback section
        if not st.session_state.feedback_submitted:
            st.markdown("---")
            st.subheader("📝 Provide Feedback")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("👍 Good Query", type="primary", use_container_width=True):
                    feedback_data = {
                        "query_id": query_data['query_id'],
                        "natural_language": query_data['natural_language'],
                        "generated_sql": query_data['generated_sql'],
                        "feedback": "thumbs_up"
                    }
                    
                    result, error = make_api_request("/feedback", "POST", feedback_data)
                    if result:
                        st.success("✅ Positive feedback submitted!")
                        st.session_state.feedback_submitted = True
                        st.rerun()
                    else:
                        st.error(f"Failed to submit feedback: {error}")
            
            with col2:
                if st.button("👎 Needs Improvement", use_container_width=True):
                    # Show correction form
                    st.markdown("### Provide Corrections")
                    corrected_sql = st.text_area(
                        "Corrected SQL Query:",
                        value=query_data['generated_sql'],
                        height=100
                    )
                    comments = st.text_area("Comments (optional):", height=60)
                    
                    if st.button("Submit Correction"):
                        feedback_data = {
                            "query_id": query_data['query_id'],
                            "natural_language": query_data['natural_language'],
                            "generated_sql": query_data['generated_sql'],
                            "feedback": "thumbs_down",
                            "corrected_sql": corrected_sql,
                            "comments": comments
                        }
                        
                        result, error = make_api_request("/feedback", "POST", feedback_data)
                        if result:
                            st.success("✅ Feedback with corrections submitted!")
                            st.session_state.feedback_submitted = True
                            st.rerun()
                        else:
                            st.error(f"Failed to submit feedback: {error}")
        
        # Display query results
        if st.session_state.query_results:
            st.markdown("---")
            st.subheader("🔍 Query Results")
            
            results = st.session_state.query_results
            
            if results['success']:
                if 'data' in results and results['data']:
                    df = pd.DataFrame(results['data'])
                    st.dataframe(df, use_container_width=True)
                    st.info(f"Returned {results['row_count']} rows")
                    
                    # Download option
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info(results.get('message', 'Query executed successfully'))
            else:
                st.error("Query execution failed")

with tab2:
    st.header("📊 Database Schema")
    
    with st.spinner("Loading database schema..."):
        schema_data, schema_error = make_api_request("/schema")
        
        if schema_data:
            st.success(f"Found {len(schema_data['tables'])} tables")
            
            for table in schema_data['tables']:
                with st.expander(f"📋 Table: {table['table_name']}"):
                    columns_df = pd.DataFrame(table['columns'])
                    st.dataframe(columns_df, use_container_width=True)
        else:
            st.error(f"Failed to load schema: {schema_error}")

with tab3:
    st.header("📈 Query Analytics")
    
    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    # Get statistics
    stats_data, stats_error = make_api_request("/feedback-stats")
    
    if stats_data:
        # Feedback distribution
        if stats_data.get('statistics'):
            st.subheader("👍👎 Feedback Distribution")
            
            feedback_df = pd.DataFrame(stats_data['statistics'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(
                    feedback_df.set_index('feedback')['count'], 
                    use_container_width=True
                )
            with col2:
                pie_data = feedback_df.set_index('feedback')['count']
                st.pie_chart(pie_data)
        
        # Recent feedback
        if stats_data.get('recent_feedback'):
            st.subheader("🕒 Recent Feedback")
            recent_df = pd.DataFrame(stats_data['recent_feedback'])
            st.dataframe(recent_df, use_container_width=True)
    else:
        st.error(f"Failed to load analytics: {stats_error}")

with tab4:
    st.header("⚙️ Settings & Configuration")
    
    st.subheader("🔧 System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Database Settings**")
        st.info("MySQL Database: Connected")
        st.info("ChromaDB: Vector storage active")
        
        # Database connection test
        if st.button("🔍 Test Database Connection"):
            health_data, health_error = make_api_request("/health")
            if health_data:
                st.success("✅ All services connected")
            else:
                st.error("❌ Connection issues detected")
    
    with col2:
        st.markdown("**AI Model Settings**")
        st.info("LLM: llama3.2:3b-instruct-q4_0")
        st.info("Embeddings: all-MiniLM-L6-v2")
        
        # Model parameters (display only)
        st.slider("Temperature", 0.0, 1.0, 0.1, disabled=True)
        st.slider("Max Tokens", 100, 1000, 500, disabled=True)
    
    st.subheader("📊 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Training Data**")
        if st.button("📥 Export Training Data"):
            st.info("Feature coming soon: Export feedback data for model training")
        
        if st.button("🧹 Clear Feedback Data"):
            st.warning("This will remove all feedback data. Are you sure?")
    
    with col2:
        st.markdown("**System Maintenance**")
        if st.button("🔄 Restart Services"):
            st.info("Feature coming soon: Service restart capability")
        
        if st.button("📋 View Logs"):
            st.info("Feature coming soon: System logs viewer")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Text2SQL Generator with Human-in-the-Loop Feedback</p>
    <p>Powered by Llama 3.2, ChromaDB, and MySQL</p>
</div>
""", unsafe_allow_html=True)