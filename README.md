# Bypass Paywalls Clean - Extension Chrome

Une extension Chrome puissante pour bypass les paywalls des sites d'actualités, optimisée pour Le Figaro et d'autres sites français.

## 🚀 Fonctionnalités

- ✅ **Bypass automatique** des paywalls de Le Figaro
- 🍪 **Suppression intelligente des cookies** de tracking
- 🤖 **User-Agent Googlebot** pour contourner les restrictions
- 📊 **Interface moderne** avec statistiques détaillées
- 🔄 **Redirection automatique** vers archive.is si nécessaire
- 📈 **Backend API** pour tracking et configuration
- 🛡️ **Techniques multiples** : DOM manipulation, headers, scripts

## 📁 Structure du projet

```
/app/
├── manifest.json           # Configuration de l'extension Chrome
├── background.js           # Service worker (gestion des requêtes)
├── contentScript.js        # Script injecté dans les pages web
├── contentScript_once.js   # Script d'injection précoce
├── popup.html             # Interface utilisateur de l'extension
├── popup.js               # Logique de l'interface
├── sites.js               # Configuration des sites supportés
├── rules.json             # Règles de filtrage des requêtes
├── icons/                 # Icônes de l'extension
├── backend/               # API Backend FastAPI
│   ├── server.py          # Serveur API
│   └── .env               # Variables d'environnement
└── README.md              # Ce fichier
```

## 🔧 Installation

### 1. Installation de l'extension Chrome

1. Ouvrez Chrome et allez sur `chrome://extensions/`
2. Activez le **Mode développeur** (coin supérieur droit)
3. Cliquez sur **Charger l'extension non empaquetée**
4. Sélectionnez le dossier `/app` de ce projet
5. L'extension apparaît dans votre barre d'outils Chrome

### 2. Configuration du Backend (optionnel)

Le backend permet de tracker les statistiques et gérer les configurations :

```bash
# Le serveur est déjà démarré automatiquement via supervisor
# URL: http://localhost:8001/api
```

## 🎯 Utilisation

### Pour Le Figaro

1. Visitez un article Le Figaro avec paywall
2. L'extension fonctionne automatiquement :
   - Supprime les cookies de tracking
   - Change le User-Agent en Googlebot
   - Manipule le DOM pour révéler le contenu
   - Bloque les scripts de paywall

3. Si le paywall persiste, cliquez sur l'icône de l'extension :
   - **Supprimer les cookies** : Force la suppression
   - **Actualiser la page** : Recharge avec bypass
   - **Voir version archivée** : Redirige vers archive.is

### Interface de l'extension

- **Toggle On/Off** : Activer/désactiver l'extension
- **Statistiques** : Articles débloqués aujourd'hui/au total
- **Actions rapides** : Boutons pour forcer le bypass
- **Support sites** : Indique si le site actuel est supporté

## 🔬 Techniques de Bypass

### 1. Manipulation des Headers HTTP
```javascript
// User-Agent Googlebot
'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'

// Referer Google
'https://www.google.com/'
```

### 2. Suppression des Cookies
```javascript
// Cookies supprimés pour Le Figaro
['PHPSESSID', '_ga', '_gid', 'tarteaucitron', 'figaro_paywall', 'premium_views']
```

### 3. Manipulation du DOM
```javascript
// Suppression des éléments paywall
'.fig-paywall', '.fig-premium-paywall', '.subscription-banner'

// Révélation du contenu
'.fig-content-body', '.fig-article__content'
```

### 4. Blocage de Scripts
```javascript
// Scripts bloqués
'*paywall*', '*subscription*', '*premium*'
```

### 5. Extraction JSON-LD
```javascript
// Récupération du contenu via structured data
script[type="application/ld+json"]
```

## 📊 API Backend

### Endpoints disponibles

- `GET /api/` - Informations de l'API
- `POST /api/bypass-log` - Logger les actions de bypass
- `GET /api/bypass-stats` - Statistiques de bypass
- `GET /api/site-config/{domain}` - Configuration d'un site
- `POST /api/update-rules` - Mettre à jour les règles
- `GET /api/supported-sites` - Sites supportés
- `POST /api/test-bypass` - Tester le bypass d'une URL

## 🎯 Test immédiat

Pour tester l'extension immédiatement :

1. **Chargez l'extension dans Chrome** (instructions ci-dessus)
2. **Visitez Le Figaro** : https://www.lefigaro.fr/
3. **Trouvez un article premium** (marqué par une icône premium)
4. **L'extension agit automatiquement** pour tenter de contourner le paywall
5. **Utilisez le popup** de l'extension pour des actions manuelles si nécessaire

## ⚖️ Avertissement légal

Cette extension est fournie à des fins éducatives uniquement. L'utilisation de cette extension pour contourner les paywalls de sites payants peut violer les conditions d'utilisation de ces sites. L'utilisateur est seul responsable de l'utilisation qu'il fait de cette extension.

---

**Version**: 3.8.8.0  
**Dernière mise à jour**: Août 2025  
**Fait avec ❤️ pour la liberté d'information**
