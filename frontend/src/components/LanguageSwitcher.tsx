import { useTranslation } from 'react-i18next';

const LANGUAGES = [
  { code: 'es', flag: 'https://flagcdn.com/w20/es.png', label: 'ES' },
  { code: 'en', flag: 'https://flagcdn.com/w20/us.png', label: 'EN' },
  { code: 'pt', flag: 'https://flagcdn.com/w20/br.png', label: 'PT' },
];

export const LanguageSwitcher = () => {
  const { i18n } = useTranslation();
  const current = LANGUAGES.find(l => l.code === i18n.language) || LANGUAGES[0];

  return (
    <div className="relative group">
      <button className="flex items-center gap-2 px-2 py-1.5 rounded-lg text-sm text-text-secondary hover:text-white hover:bg-zinc-800 transition">
        <img src={current.flag} alt={current.label} className="w-4 h-3 object-cover rounded-[2px]" />
        <span className="font-mono text-xs">{current.label}</span>
        <span className="text-zinc-600 text-xs">▾</span>
      </button>
      {/* Dropdown */}
      <div className="absolute right-0 top-full mt-1 w-28 bg-zinc-900 border border-zinc-800 rounded-xl shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-150 z-50 overflow-hidden">
        {LANGUAGES.map(lang => (
          <button
            key={lang.code}
            onClick={() => i18n.changeLanguage(lang.code)}
            className={`w-full flex items-center gap-2 px-3 py-2 text-sm transition hover:bg-zinc-800 ${
              i18n.language === lang.code ? 'text-primary font-semibold' : 'text-text-secondary'
            }`}
          >
            <img src={lang.flag} alt={lang.label} className="w-4 h-3 object-cover rounded-[2px]" />
            <span className="font-mono text-xs">{lang.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
