# Shkarkon modelet e gjuhes Tesseract ("best" — me te sakta) ne tessdata/ te projektit.
# Ruajtur lokalisht ne projekt (jo ne Program Files) qe te mos duhet admin per t'i shtuar.
$dir = Join-Path $PSScriptRoot "..\tessdata"
New-Item -ItemType Directory -Force -Path $dir | Out-Null

$files = @{
    "sqi.traineddata" = "https://github.com/tesseract-ocr/tessdata_best/raw/main/sqi.traineddata"
    "eng.traineddata" = "https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata"
    "osd.traineddata" = "https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata"
}

foreach ($name in $files.Keys) {
    $dest = Join-Path $dir $name
    Write-Host "Duke shkarkuar $name..."
    Invoke-WebRequest -Uri $files[$name] -OutFile $dest -UseBasicParsing
}

Write-Host "Gati."
