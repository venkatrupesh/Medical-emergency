from languages import TRANSLATIONS, LANGUAGES

# Test if translations exist
print("Testing translations...")
print(f"\nAvailable languages: {list(LANGUAGES.keys())}")

# Test Hindi
print(f"\nHindi 'home': {TRANSLATIONS['hi']['home']}")
print(f"Hindi 'emergency': {TRANSLATIONS['hi']['emergency']}")
print(f"Hindi 'report_emergency': {TRANSLATIONS['hi']['report_emergency']}")

# Test Telugu
print(f"\nTelugu 'home': {TRANSLATIONS['te']['home']}")
print(f"Telugu 'emergency': {TRANSLATIONS['te']['emergency']}")

# Test Tamil
print(f"\nTamil 'home': {TRANSLATIONS['ta']['home']}")
print(f"Tamil 'emergency': {TRANSLATIONS['ta']['emergency']}")

print("\n✓ All translations loaded successfully!")
