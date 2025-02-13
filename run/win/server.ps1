Set-Location -Path (Join-Path -Path (Get-Location).Parent.Parent -ChildPath "examples/calculator")
echo Y | python -m http.server 8080