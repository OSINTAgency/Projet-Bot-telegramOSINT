# OSINT Bot Telegram

Un bot Telegram pour effectuer des recherches OSINT et générer des rapports détaillés.

## Commandes disponibles

- `/start` - Démarre le bot
- `/help` - Affiche cette aide
- `/search <query>` - Effectue une recherche OSINT
- `/search_twitter <query>` - Recherche sur Twitter
- `/search_whois <domain>` - Recherche Whois pour un domaine
- `/search_ip <ip_address>` - Recherche d'informations sur une adresse IP
- `/search_breaches <email>` - Recherche de fuites de données pour une adresse email
- `/search_engine <query>` - Recherche sur les moteurs de recherche
- `/search_financial <company>` - Recherche financière sur une entreprise
- `/search_news <query>` - Recherche d'actualités sur Google Actualités
- `/host <domain>` - Utilise l'outil host pour obtenir des informations DNS
- `/nslookup <query>` - Utilise l'outil nslookup pour obtenir des informations DNS
- `/dnseum <query>` - Utilise l'outil dnseum
- `/bile_suite <query>` - Utilise l'outil bile-suite
- `/tld_expand <query>` - Utilise l'outil tld-expand pour obtenir des informations sur les TLD
- `/report <query>` - Génère un rapport détaillé
- `/history` - Affiche l'historique de vos recherches
- `/subscribe <query>` - Abonnez-vous aux alertes pour une requête spécifique
- `/unsubscribe <query>` - Désabonnez-vous des alertes
- `/pay_with_crypto <plan>` - Procédez au paiement en crypto pour les fonctionnalités premium

## Déploiement sur Vercel

1. Clonez le repo.
2. Installez Vercel CLI globalement : `npm install -g vercel`.
3. Connectez-vous à Vercel : `vercel login`.
4. Déployez le projet : `vercel`.

## Configuration

Ajoutez les clés API et les configurations nécessaires dans `config.py`.

## Tarification

### Essai Gratuit / Freemium

- Recherches OSINT de Base : Limitées à 5 recherches par mois.
- Rapports de Synthèse : Limité à 1 rapport par mois.

### Abonnements

1. **Plan de Base** : 10 $/mois ou 100 $/an
2. **Plan Pro** : 25 $/mois ou 250 $/an
3. **Plan Entreprise** : 50 $/mois ou 500 $/an

### Paiement à la Carte

- Recherche OSINT unique : 2 $ par recherche
- Rapport détaillé unique : 10 $ par rapport
