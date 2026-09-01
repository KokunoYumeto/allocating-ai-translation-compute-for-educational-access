param([int[]]$Pages = @(11,12,13,14,33,34,39,85,86))
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$taskCanon = Join-Path $taskRoot 'downloads/mr-Deva-IN/canon'
foreach ($page in $Pages) {
    $stem = Join-Path $taskCanon "pages/balbharati8-$page"
    & pdftoppm -f $page -l $page -r 160 -singlefile -png (Join-Path $taskCanon 'balbharati-8-mr.pdf') $stem
    if ($LASTEXITCODE -ne 0) { throw "Rendering page $page failed" }
    & tesseract "$stem.png" (Join-Path $taskCanon "ocr/balbharati8-$page") --tessdata-dir (Join-Path $taskCanon 'tessdata') -l mar+eng --psm 3
    if ($LASTEXITCODE -ne 0) { throw "OCR page $page failed" }
    Write-Output "OCR ready: physical PDF page $page"
}
