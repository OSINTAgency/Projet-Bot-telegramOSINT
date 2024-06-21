import whois

try:
    domain_info = whois.whois("example.com")
    print(domain_info)
except Exception as e:
    print(f"Erreur Whois: {str(e)}")
