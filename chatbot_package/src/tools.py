import sqlite3
import os
try:
    import plotly.graph_objs as go
    import plotly.io as pio
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: Plotly not available, charts will be text-based")

try:
    from .utils import convert_to_json, json_to_markdown_table
except ImportError:
    # Fallback functions if utils import fails
    def convert_to_json(data):
        return str(data)
    def json_to_markdown_table(data):
        return str(data)

# function calling
# avialable tools
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_table_schema",
            "description": "Get the schema and column names of the main_table to understand the dataset structure",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_sqlite_query",
            "description": "Execute SQL query on the uploaded dataset to fetch and analyze data",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "Complete and correct SQL query to fulfill user request. The table name is 'main_table'.",
                    }
                },
                "required": ["sql_query"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "plot_chart",
            "description": "Create visualizations from data. Use this after running a SQL query to get the data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "plot_type": {
                        "type": "string",
                        "description": "Type of chart to create",
                        "enum": ["bar", "line", "scatter", "pie", "histogram"]
                    },
                    "sql_query": {
                        "type": "string",
                        "description": "SQL query to get data for the chart. This will be executed to get the actual data."
                    },
                    "plot_title": {
                        "type": "string",
                        "description": "Descriptive title for the plot",
                    },
                    "x_label": {
                        "type": "string",
                        "description": "Label for the x axis",
                    },
                    "y_label": {
                        "type": "string",
                        "description": "Label for the y axis",
                    },
                    "x_column": {
                        "type": "string",
                        "description": "Name of the column to use for x-axis values"
                    },
                    "y_column": {
                        "type": "string", 
                        "description": "Name of the column to use for y-axis values"
                    }
                },
                "required": ["plot_type", "sql_query", "plot_title", "x_label", "y_label", "x_column", "y_column"],
            },
        }
    }
]


async def get_table_schema():
    """Get the schema and column information of the main_table"""
    try:
        # Get database path from environment
        db_path = os.getenv('CHATBOT_DB_PATH', '/tmp/dataset_1.db')
        print(f"Getting schema for database: {db_path}")
        
        if not os.path.exists(db_path):
            return "Error: Database not found. Please upload a dataset first."
        
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Get table schema
        cursor.execute("PRAGMA table_info(main_table)")
        schema_info = cursor.fetchall()
        
        # Get sample data to understand the content
        cursor.execute("SELECT * FROM main_table LIMIT 3")
        sample_data = cursor.fetchall()
        
        # Get column names
        cursor.execute("SELECT * FROM main_table LIMIT 1")
        column_names = [desc[0] for desc in cursor.description]
        
        connection.close()
        
        if not schema_info:
            return "Error: main_table not found in database."
        
        # Format schema information
        schema_text = "## Dataset Schema\n\n"
        schema_text += "**Table:** main_table\n\n"
        schema_text += "**Columns:**\n"
        
        for info in schema_info:
            col_name, col_type, not_null, default_val, pk = info
            schema_text += f"- `{col_name}` ({col_type})\n"
        
        schema_text += f"\n**Sample Data (first 3 rows):**\n"
        for i, row in enumerate(sample_data):
            schema_text += f"Row {i+1}: "
            for j, col_name in enumerate(column_names):
                schema_text += f"{col_name}={row[j]}, "
            schema_text = schema_text.rstrip(", ") + "\n"
            
        return schema_text
        
    except Exception as error:
        print(f"Error getting schema: {error}")
        return f"Error getting schema: {error}"


async def run_postgres_query(sql_query, markdown=True):
    connection = None  # Initialize connection variable outside the try block
    try:
        # Establish the connection
        connection = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        print("Connected to the database!")

        # Create a cursor object
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(sql_query)

        # Fetch the column names
        column_names = [desc[0] for desc in cursor.description]

        # Fetch all rows
        result = cursor.fetchall()
        if markdown:
            # get result in json
            json_data = convert_to_json(result,column_names)
            markdown_data = json_to_markdown_table(json_data)

            return markdown_data

        return result, column_names
    except (Exception, psycopg2.Error) as error:
        print("Error while executing the query:", error)
        if markdown:
            return f"Error while executing the query: {error}"
        return [], []

    finally:
        # Close the cursor and connection
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


async def run_sqlite_query(sql_query, markdown=True):
    """Execute SQL query on the uploaded dataset"""
    connection = None
    try:
        # Get database path from environment (set by backend when dataset is uploaded)
        db_path = os.getenv('CHATBOT_DB_PATH', '/tmp/dataset_1.db')
        print(f"Using database: {db_path}")
        
        if not os.path.exists(db_path):
            return f"Error: Database not found at {db_path}. Please upload a dataset first."
        
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(sql_query)

        # Fetch the column names
        column_names = [desc[0] for desc in cursor.description]

        # Fetch all rows
        result = cursor.fetchall()
        
        if markdown:
            # Convert to JSON format for better display
            json_data = convert_to_json(result, column_names)
            
            # Limit results to prevent token overflow
            if len(result) > 20:
                limited_json = json_data[:20]
                markdown_data = json_to_markdown_table(limited_json)
                markdown_data += f"\n\n*(Showing first 20 of {len(result)} rows)*"
                return markdown_data
            else:
                markdown_data = json_to_markdown_table(json_data)
                return markdown_data
        
        return result, column_names
        
    except Exception as error:
        print("Error while executing SQLite query:", error)
        if markdown:
            return f"Error while executing the query: {error}"
        return [], []

    finally:
        if connection:
            connection.close()


async def plot_chart(plot_type, sql_query, plot_title, x_label, y_label, x_column, y_column):
    """Create charts from SQL query results"""
    try:
        # Get database path from environment
        db_path = os.getenv('CHATBOT_DB_PATH', '/tmp/dataset_1.db')
        
        if not os.path.exists(db_path):
            return "Error: Database not found. Please upload a dataset first."
        
        # Execute SQL query to get data
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(sql_query)
        
        # Fetch column names and data
        column_names = [desc[0] for desc in cursor.description]
        result = cursor.fetchall()
        connection.close()
        
        if not result:
            return "No data returned from query."
        
        # Convert to dictionary format for easier processing
        data_dicts = []
        for row in result:
            row_dict = {}
            for i, col_name in enumerate(column_names):
                row_dict[col_name] = row[i]
            data_dicts.append(row_dict)
        
        # Extract x and y values using column names
        try:
            x_values = [str(row[x_column]) for row in data_dicts]
            y_values = [float(row[y_column]) if row[y_column] is not None else 0 for row in data_dicts]
        except KeyError as e:
            return f"Error: Column '{e}' not found in query results. Available columns: {column_names}"
        except (ValueError, TypeError) as e:
            return f"Error converting data types: {e}"
        
        if not PLOTLY_AVAILABLE:
            # Return text-based chart description
            chart_text = f"\n## {plot_title}\n"
            chart_text += f"**{x_label}** vs **{y_label}**\n\n"
            for i, (x, y) in enumerate(zip(x_values, y_values)):
                chart_text += f"- {x}: {y}\n"
            return chart_text
        
        # Create Plotly chart
        if plot_type == "bar":
            fig = go.Figure(data=[go.Bar(x=x_values, y=y_values)])
        elif plot_type == "line":
            fig = go.Figure(data=[go.Scatter(x=x_values, y=y_values, mode='lines+markers')])
        elif plot_type == "scatter":
            fig = go.Figure(data=[go.Scatter(x=x_values, y=y_values, mode='markers')])
        elif plot_type == "pie":
            fig = go.Figure(data=[go.Pie(labels=x_values, values=y_values)])
        elif plot_type == "histogram":
            fig = go.Figure(data=[go.Histogram(x=y_values)])
        else:
            return f"Unsupported plot type: {plot_type}"
        
        # Update layout
        fig.update_layout(
            title=plot_title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            template="plotly_white"
        )
        
        # Convert to HTML and save to file instead of returning full HTML
        chart_html = pio.to_html(fig, include_plotlyjs='cdn')
        
        # Save chart to file
        chart_filename = f"chart_{hash(plot_title)}_{plot_type}.html"
        chart_path = f"/tmp/{chart_filename}"
        
        with open(chart_path, 'w') as f:
            f.write(chart_html)
        
        # Return concise summary instead of full HTML
        summary = f"✅ {plot_type.title()} chart '{plot_title}' created successfully!\n"
        summary += f"📊 Data points: {len(x_values)}\n"
        summary += f"📈 Range: {min(y_values):.2f} to {max(y_values):.2f}\n"
        summary += f"💾 Chart saved to: {chart_path}"
        
        return summary
        
    except Exception as error:
        print(f"Error creating chart: {error}")
        return f"Error creating chart: {error}"
