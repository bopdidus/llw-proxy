# LLM Gateway

Une passerelle (gateway) FastAPI placée devant un LLM local (Ollama). Avant d'envoyer un prompt au modèle, elle détecte les données sensibles (emails, IBAN, ...) à l'aide de règles décrites dans un petit langage dédié (DSL), puis les masque.

## Fonctionnement

```
Client ──POST /──▶ FastAPI ──▶ analyse (policy.cfg) ──▶ masquage ──▶ Ollama ──▶ réponse
```

1. Le client envoie un prompt à `POST /`.
2. `policy.cfg` est compilé en expressions régulières par `dsl_compiler.py` (grammaire dans `grammar.lark`).
3. Les données qui correspondent aux règles sont remplacées dans le prompt.
4. Le prompt masqué est envoyé au modèle via Ollama, et la réponse est renvoyée au client.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `main.py` | Application FastAPI (route `POST /`) |
| `utils.py` | `analyse_text` (compile les règles), `replace` (masquage), `get_response` (appel à Ollama) |
| `dsl_compiler.py` | Compilateur du DSL : lit la grammaire, transforme `policy.cfg` en regex |
| `grammar.lark` | Grammaire Lark (LALR) du DSL |
| `policy.cfg` | Politique : ensembles de caractères et règles de détection |

## Le DSL de politique

Un fichier `policy.cfg` contient un statement par ligne : des **ensembles** (`nom: ...`) et des **règles** (`NOM = ...`).

```
digit: 0...9
letter: a...z, A...Z
alphanumeric: letter, digit, _, ., -

EMAIL = alphanumeric+ @ alphanumeric+ . letter{2,4}
IBAN = digit{10,34}
```

### Ensembles
- Plage : `0...9`, `a...z`
- Caractère littéral : `_`, `.`, `-`, `'a'`
- Référence à un ensemble déjà défini : `letter`, `digit`

Un ensemble est compilé en classe de caractères, par exemple `alphanumeric` → `[a-zA-Z0-9_\.\-]`.

### Règles
Une règle est une suite d'éléments, chacun pouvant porter un quantificateur :
- un ensemble (`alphanumeric`, ou `[alphanumeric]`) ou un caractère littéral (`@`, `.`)
- quantificateurs : `+`, `*`, `?`, `{n}`, `{n,}`, `{n,m}`

Les ensembles doivent être définis avant d'être utilisés. Les littéraux sont échappés automatiquement.

### Résultat de la compilation

```
[email]: [a-zA-Z0-9_\.\-]+@[a-zA-Z0-9_\.\-]+\.[a-zA-Z]{2,4}
[iban]: [0-9]{10,34}
```

## Installation

Prérequis : Python 3.10+ et [Ollama](https://ollama.com/download) installé et lancé.

```bash
python -m venv gateway
gateway\Scripts\activate
pip install fastapi uvicorn lark ollama
ollama pull gemma4:e2b
```

Le modèle utilisé est défini dans `utils.py` (`get_response`).

## Lancer

```bash
uvicorn main:app --reload
```

## Utilisation

Le corps de la requête est une chaîne JSON.

```bash
curl -X POST http://127.0.0.1:8000/ -H "Content-Type: application/json" -d "\"Mon email est jean.dupont@exemple.com\""
```

## Ajouter une règle

Ajoutez simplement une ligne dans `policy.cfg`, par exemple :

```
PHONE = digit{10}
```

Aucune modification du code n'est nécessaire.

## Limites connues

- Les règles sont simples : `IBAN = digit{10,34}` ne vérifie ni le code pays ni la clé de contrôle.
- Pas de bornes de mot : une règle peut matcher au milieu d'une suite plus longue.
- La politique est recompilée à chaque requête.
