mkdir -p ~/.streamlit/

echo "\
[theme]
primaryColor = \"#FF6B6B\"\n\
backgroundColor = \"#FFFFFF\"\n\
secondaryBackgroundColor = \"#F0F2F6\"\n\
textColor = \"#262730\"\n\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = \$PORT\n\
" > ~/.streamlit/config.toml
