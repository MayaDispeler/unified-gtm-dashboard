import re
with open('gtm_dashboard_final.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the cc-n spans (these are the report numbers like #4, #100 that overlap with the new i icon)
text = re.sub(r'<span class="cc-n">.*?</span>', '', text)

# Modify the deal-badge textContent line to include "100 Reports"
# The original line looks something like:
# $('deal-badge').textContent = fN(k.total_deals) + ' deals';
# Or: $('deal-badge').textContent = (ORIG.kpi.total_deals/1000).toFixed(0)+'K deals';
# I'll just replace the innerHTML/textContent assignment directly.
text = re.sub(
    r"(\$\('deal-badge'\)\.(?:textContent|innerHTML)\s*=\s*)(.*?);",
    r"\1'100 Reports | ' + \2;",
    text
)

with open('gtm_dashboard_final.html', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated gtm_dashboard_final.html successfully.')
