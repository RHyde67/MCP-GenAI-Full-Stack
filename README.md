# MCP Test Development

## Description
This repo is not for production work.

It is intended for developing and testing Model Context Protocol (MCP) severs and tools.
## Getting Started
Clone the repo.
Activate the venv.

## How to build the Chroma DB
Place the documnts in the test_docs folder.

Currently only Word docx files have been tested.
Run: ``` python ingest/chroma_ingest.py ```

This will build a chroma db, stored in the vdb folder.

A running total of document names and number of chunks is dsplayed during the process.

Currently the ingestion uses paragraph based chunking to improve the context of each chunks.

Meta data is stored, currently filename and chunk id. This allows for improved retrieval, document updates and deletions.

## How to Test the Server
To test the server by itself, without using any potentially bugged apps....

The server.py file must end like this:
```
--------------------------
 Run server
 --------------------------
if __name__ == "__main__":
    # use this line to run normally with FastMCP's built-in server:
    # mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
    # Use this line to test the standalone server using inspector.
    # python -m mcp_inspector --command python -- server.py
    mcp.run()```
```
This will run the sever in stdio mode.

Then run the inspector with:
```fastmcp dev inspector .\server.py```

To test the server tools:
1. Click 'connect' at the bottom of left menu. This will connect to the sever specified in the command line.
2. Click 'tools' on the top menu bar
3. Click 'list tools'

You will see a list of tools. Select any tool and it will appear in the next column. Fill in any required inputs and run the tool.
You will see success or fail message with details, including the tool response. The tool response is what your app will receive when it runs the tool.


#### NOTE: To run the server with your app, you will need to revert the end of the server.py file to:
```
 --------------------------
 Run server
 --------------------------
if __name__ == "__main__":
    # use this line to run normally with FastMCP's built-in server:
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
    # Use this line to test the standalone server using inspector.
    # python -m mcp_inspector --command python -- server.py
    # mcp.run()
```

## How To Run the Server and Application
### Start the MCP Server
Open a terminal to start the MCP server. In the terminal type:
``` mcp dev server.py ```
This will silently start the server contained n the server.py file.

For test purposes, multiple servers can be created in different files.

### Start the App that uses the server
open a new terminal. type:
``` streamlit run app/demo.py ```

The app will open in your browser and use the server to run the tools.


## Support
Initial dev by Richard Hyde:
richard.hyde@rwhyde.co.uk

## Roadmap
No further plans at this time. This adequately demonstartes the benfits of MCP.

## Contributing


## Authors and acknowledgment


## License


## Project status

