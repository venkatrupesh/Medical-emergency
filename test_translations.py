from languages import TRANSLATIONS, LANGUAGES
import json

print("=== Language System Test ===\n")

print("Available languages:")
for code, info in LANGUAGES.items():
    print(f"  {code}: {info['name']} {info['flag']}")

print(f"\nTelugu translations count: {len(TRANSLATIONS.get('te', {}))}")
print("\nSample Telugu translations:")
for key in list(TRANSLATIONS.get('te', {}).keys())[:15]:
    print(f"  {key}: {TRANSLATIONS['te'][key]}")

print("\n=== Testing JSON serialization ===")
test_translations = TRANSLATIONS.get('te', {}).copy()
test_translations['_currentLang'] = 'te'
json_str = json.dumps(test_translations, ensure_ascii=False)
print(f"JSON length: {len(json_str)} characters")
print(f"First 200 chars: {json_str[:200]}")
