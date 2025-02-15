install.packages("httpuv")

library(httpuv)

# Define the path to the directory containing your files
dir_path <- "path/to/your/directory"

# Define the app
app <- list(
  call = function(req) {
    # Extract the requested path
    path <- req$PATH_INFO
    
    # Default to index.html if the path is "/"
    if (path == "/") {
      path <- "/index.html"
    }
    
    # Construct the full file path
    file_path <- file.path(dir_path, path)
    
    # Check if the file exists
    if (file.exists(file_path)) {
      # Determine the MIME type based on the file extension
      mime_type <- switch(
        tools::file_ext(file_path),
        "html" = "text/html",
        "js" = "application/javascript",
        "mjs" = "application/javascript",  # Add support for .mjs files
        "css" = "text/css",
        "png" = "image/png",
        "jpg" = "image/jpeg",
        "jpeg" = "image/jpeg",
        "svg" = "image/svg+xml",
        "json" = "application/json",
        "wasm" = "application/wasm",  # Add support for .wasm files
        "text/plain" # Default MIME type
      )
      
      # Read the file content
      content <- readBin(file_path, "raw", file.info(file_path)$size)
      
      # Return the response with the correct MIME type
      list(
        status = 200L,
        headers = list('Content-Type' = mime_type),
        body = content
      )
    } else {
      # Return a 404 error if the file doesn't exist
      list(
        status = 404L,
        headers = list('Content-Type' = 'text/plain'),
        body = paste("404 Not Found:", path, "does not exist.")
      )
    }
  }
)

# Start the server on port 8080
server <- startServer("127.0.0.1", 8080, app)

# Print a message to indicate the server is running
message("Server is running at http://localhost:8080")

# To stop the server, run:
# stopServer(server)