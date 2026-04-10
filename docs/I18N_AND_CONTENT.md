# Internationalization (i18n) and catalog content

This document describes how **UI language** and **domain content** (courses, categories, seed data) are handled in SkillForge before splitting into microservices.

## UI strings (templates and Python messages)

- **Default UI language** is English: `LANGUAGE_CODE = 'en'` in `config/settings/base.py`.
- **Spanish** is available as a second locale (`LANGUAGES` includes `es`). Users can switch via Django’s language cookie / `/i18n/setlang/` when exposed in templates.
- **Middleware**: `LocaleMiddleware` is enabled so `gettext` / `{% trans %}` resolve per active language.
- **Translation files**: `LOCALE_PATHS` points to the project `locale/` directory. Run `makemessages` / `compilemessages` when adding new translatable strings.

## Catalog and database content

- **Course titles, descriptions, module names, lesson bodies, category names**, etc. are stored in the **database**, not in `.po` files.
- Seed scripts (for example `crear_datos_iniciales`) create rows with text in a chosen language. Today sample data may mix Spanish legacy content with English-oriented labels on `TextChoices` (shown in forms and admin).
- **Strategy for microservices**: treat catalog as a **content service** with an explicit **content locale** per record or per tenant, or normalize all marketing/catalog copy to one language and translate via a CMS or a dedicated translation pipeline. Until then:
  - Prefer **one primary language** for new catalog rows in production.
  - Keep **API field names** stable; localize only display strings in clients.

## API and JWT

- REST paths and JSON keys are **English** by design (`detail`, `results`, pagination metadata).
- Error messages returned by the API should stay **stable** (English) so mobile or external clients can map codes or translate client-side.

## Summary

| Layer | Approach |
|--------|-----------|
| Templates / static UI | Django i18n (`en` default, `es` optional) |
| DB catalog | Single-language content per environment unless you add locale fields |
| API | English keys and messages |
