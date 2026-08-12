$ErrorActionPreference = 'Continue'
$dest = "$PSScriptRoot\imagenes"
if (-not (Test-Path $dest)) { New-Item -ItemType Directory -Path $dest | Out-Null }

$urls = @(
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/Logo_blanco-1-scaled.png',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/TripAdvisor_Logo.svg.png',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/Booking.com_Logo.svg.png',
  'https://soldeoro.com.pe/wp-content/uploads/2023/06/Firma-staff-soldeoro2-1.png',
  'https://soldeoro.com.pe/wp-content/uploads/2026/05/PAQUETES-PROMOCIONALES-SDO-22.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/2_2_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/3_3_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/4_4_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/5_5_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/6_6_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/7_7_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/8_8_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/9_9_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/10_10_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/11_11_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/12_12_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/13_13_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/14_14_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/21_21_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/23_23_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/24_24_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/31_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/32_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/33_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/34_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/35_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/37_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/38_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/39_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/40_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/47_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/48_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/49_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/50_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/52_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO_11zon-1.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-1_2_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-2_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-3_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-3_11zon-1.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-3_11zon-2.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-5_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/JUNIOR-SUITE_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/JUNIOR-SUITE-TWIN_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-4_16_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-5_15_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-6_14_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-7_13_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-8_12_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-9_11_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-10_10_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-11_9_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-12_8_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-13_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-15_11zon-2.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FOTOS-WEB-SOL-DE-ORO-16_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/FACHADA.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/the-hotel-v13828831_ED.webp',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/PISCINA-WEB.webp',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/MG_3999_ED_5_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/MG_3965_ED_3_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/IMG_3914_ED_16_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/IMG_8388_25_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/IMG_8383_22_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/IMG_3832_ED_9_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/IMG_3856_ED_10_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/EJECUTIVO-II-HERRADURA_4_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/EJECUTIVO-II-AUDITORIO_2_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/EJECUTIVO-II-BANQUETE_3_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/MG_2145_ED-v2_5_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/MG_2211_ED_6_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/EJECUTIVO-III-y-mesas-laterales-1.jpeg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/IMG_2212_ED_9_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/Empresariales-Aula-1-1_4_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/Empresariales-Aula-5-1_5_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/EMPRESARIALES-II_10_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/EMPRESARIALES-I_7_11zon.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/IMG_2226_ED_8_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/Empresariales-Aud-8-1_3_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/MG_2636_edi2-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2019/08/MG_3383_ED.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/MG_2588_edi2-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2019/08/SALA-SOL-DE-ORO-1.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2019/08/IMG_4033_ED.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/SOL-DE-ORO-MESAS-REDONDAS-1.jpeg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/MG_1800_ED_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/MG_3999_ED_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/MG_2135_ED_11zon-scaled.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2019/08/Piso-I.png',
  'https://soldeoro.com.pe/wp-content/uploads/2019/08/Piso-II.png',
  'https://soldeoro.com.pe/wp-content/uploads/2019/08/Piso-12.png',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/image-1.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/image-2.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/image-3.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/image-4.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/10/image-5.jpg',
  'https://soldeoro.com.pe/wp-content/uploads/2025/11/fotos-blog-1.png',
  'https://soldeoro.com.pe/wp-content/uploads/2025/11/fotos.png'
)

$total = $urls.Count
$ok = 0
$fail = 0
$failed = @()
$i = 0

foreach ($url in $urls) {
  $i++
  $name = Split-Path $url -Leaf
  $out = Join-Path $dest $name
  if (Test-Path $out) {
    Write-Output "[$i/$total] skip (already exists): $name"
    $ok++
    continue
  }
  try {
    Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing -TimeoutSec 30 -ErrorAction Stop
    $size = (Get-Item $out).Length
    Write-Output "[$i/$total] OK ($([math]::Round($size/1KB,1)) KB): $name"
    $ok++
  } catch {
    Write-Output "[$i/$total] FAIL: $name -- $($_.Exception.Message)"
    $fail++
    $failed += $url
  }
}

Write-Output ""
Write-Output "=============================="
Write-Output "TOTAL: $total | OK: $ok | FAIL: $fail"
if ($failed.Count -gt 0) {
  Write-Output ""
  Write-Output "URLs fallidas:"
  $failed | ForEach-Object { Write-Output "  - $_" }
}
