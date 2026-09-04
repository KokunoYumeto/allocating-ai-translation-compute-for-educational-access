param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$scorePath = Join-Path $Root 'structured\GLOBAL_TARGET_SCORE_TABLE_v3.csv'
$mismatchPath = Join-Path $Root 'qa\COUNTRY_TERRITORY_BINDING_MISMATCHES_v1.csv'
$qaPath = Join-Path $Root 'qa\COUNTRY_TERRITORY_BINDING_AUDIT_v1.json'
$rows = Import-Csv -LiteralPath $scorePath
$mismatches = [System.Collections.Generic.List[object]]::new()
$parsedRegionCount = 0
$unresolvedCount = 0

foreach ($row in $rows) {
    $tag = [string]$row.language_tag
    $match = [regex]::Match($tag, '^[A-Za-z]{2,3}(?:-[A-Za-z]{4})?-(?<region>[A-Z]{2})(?:-|:|$)')
    if ($match.Success) {
        $parsedRegionCount++
        $region = $match.Groups['region'].Value
        try {
            $expected = ([System.Globalization.RegionInfo]::new($region)).ThreeLetterISORegionName.ToUpperInvariant()
        }
        catch {
            $expected = ''
        }
        if ($expected -and $row.country_iso3 -and $expected -ne $row.country_iso3) {
            $mismatches.Add([pscustomobject]@{
                check = 'BCP47_REGION_VS_COUNTRY_ISO3'
                edition_target_id = $row.edition_target_id
                language_tag = $tag
                expected_country_iso3 = $expected
                observed_country_iso3 = $row.country_iso3
                label = $row.label
                territory_community = $row.territory_community
                primary_order_eligible = $row.primary_order_eligible
            })
        }
    }
    if ($tag -match 'unresolved' -or $row.edition_target_id -match 'unresolved') {
        $unresolvedCount++
        if ($row.country_iso3) {
            $mismatches.Add([pscustomobject]@{
                check = 'UNRESOLVED_IDENTITY_MUST_NOT_RECEIVE_COUNTRY_FACTOR'
                edition_target_id = $row.edition_target_id
                language_tag = $tag
                expected_country_iso3 = ''
                observed_country_iso3 = $row.country_iso3
                label = $row.label
                territory_community = $row.territory_community
                primary_order_eligible = $row.primary_order_eligible
            })
        }
    }
}

$knownExpected = @{
    'edition-target:lang:ta-Taml-LK:community:malayaga' = 'LKA'
    'edition-target:regional:ru-Cyrl-EE' = 'EST'
    'edition-target:lang:unresolved-tag:amazonian-kichwa-in-peru:peru-amazonian-kichwa-in-peru-educat' = ''
    'edition-target:lang:unresolved-tag:chilean-quechua-exact-local-variety-required:chile-chilean-quechua-exact-local-va' = ''
}
$byId = @{}
foreach ($row in $rows) { $byId[$row.edition_target_id] = $row }
$knownChecks = [System.Collections.Generic.List[object]]::new()
foreach ($targetId in $knownExpected.Keys) {
    $expected = $knownExpected[$targetId]
    $present = $byId.ContainsKey($targetId)
    $observed = if ($present) { [string]$byId[$targetId].country_iso3 } else { '' }
    $pass = $present -and $observed -eq $expected
    $knownChecks.Add([pscustomobject]@{
        edition_target_id = $targetId
        expected_country_iso3 = $expected
        observed_country_iso3 = $observed
        target_present = $present
        pass = $pass
    })
    if (-not $pass) {
        $mismatches.Add([pscustomobject]@{
            check = 'KNOWN_REGRESSION_TARGET'
            edition_target_id = $targetId
            language_tag = if ($present) { $byId[$targetId].language_tag } else { '' }
            expected_country_iso3 = $expected
            observed_country_iso3 = $observed
            label = if ($present) { $byId[$targetId].label } else { '' }
            territory_community = if ($present) { $byId[$targetId].territory_community } else { '' }
            primary_order_eligible = if ($present) { $byId[$targetId].primary_order_eligible } else { '' }
        })
    }
}

$mismatchFields = @('check','edition_target_id','language_tag','expected_country_iso3','observed_country_iso3','label','territory_community','primary_order_eligible')
if ($mismatches.Count -eq 0) {
    $mismatchCsv = [pscustomobject]@{
        check='';edition_target_id='';language_tag='';expected_country_iso3='';observed_country_iso3='';label='';territory_community='';primary_order_eligible=''
    } | ConvertTo-Csv -NoTypeInformation
}
else {
    $mismatchCsv = $mismatches | Select-Object $mismatchFields | ConvertTo-Csv -NoTypeInformation
}
[System.IO.File]::WriteAllLines($mismatchPath, [string[]]$mismatchCsv, [System.Text.UTF8Encoding]::new($false))

$qa = [ordered]@{
    schema = 'interlanguage/country-territory-binding-audit/1.0.0'
    generated_at_utc = [DateTime]::UtcNow.ToString('o')
    status = if ($mismatches.Count -eq 0) { 'PASS' } else { 'FAIL' }
    input = [ordered]@{
        path = 'structured/GLOBAL_TARGET_SCORE_TABLE_v3.csv'
        rows = $rows.Count
        bytes = (Get-Item -LiteralPath $scorePath).Length
        sha256 = (Get-FileHash -LiteralPath $scorePath -Algorithm SHA256).Hash
    }
    checks = [ordered]@{
        valid_bcp47_region_rows_checked = $parsedRegionCount
        unresolved_identity_rows_checked = $unresolvedCount
        known_regression_checks = $knownChecks
        mismatch_count = $mismatches.Count
    }
    mismatch_output = [ordered]@{
        path = 'qa/COUNTRY_TERRITORY_BINDING_MISMATCHES_v1.csv'
        bytes = (Get-Item -LiteralPath $mismatchPath).Length
        sha256 = (Get-FileHash -LiteralPath $mismatchPath -Algorithm SHA256).Hash
    }
    interpretation = @(
        'A valid BCP-47 region subtag must agree with the country context used by the scoring model.',
        'Unresolved descriptive identities receive no country-conditioned factor.',
        'This audit does not infer a country from ethnicity or language adjectives in prose.'
    )
}
$json = $qa | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText($qaPath, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
$qa | ConvertTo-Json -Depth 8
