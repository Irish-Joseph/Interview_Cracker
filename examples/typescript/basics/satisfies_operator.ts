/**
 * Topic: The `satisfies` operator — type-check without losing specificity.
 *
 * Concepts:
 * - The problem: annotating a const with a type WIDENS it
 * - `satisfies` checks a value against a type WITHOUT using it as the
 *   value's inferred type
 * - Keeping literal types (e.g. "en" | "de") for autocomplete/lookup
 * - Typical use: config objects with a known shape
 *
 * Example output:
 *   greeting: Hello
 *   available locales: en de fr
 *   fr is a known locale: true
 */

// The shape every locale entry must follow.
interface Locale {
  greeting: string;
  code: string;
}

// The full set of allowed locale keys, defined independently so we
// can test membership later.
const SUPPORTED = ["en", "de", "fr"] as const;
type SupportedLocale = (typeof SUPPORTED)[number];

// WITHOUT satisfies: annotating the record widens `code` to `string`
// and the keys are just object keys.
// const bad: Record<string, Locale> = {...};  // codes become `string`

// WITH satisfies: the object is checked against Record<SupportedLocale, Locale>
// (every supported locale present, each entry shaped like Locale)
// ...but the inferred type stays precise:
//   - keys are exactly "en" | "de" | "fr"
//   - locales.en.code is the literal "en"
const locales = {
  en: { greeting: "Hello", code: "en" },
  de: { greeting: "Hallo", code: "de" },
  fr: { greeting: "Bonjour", code: "fr" },
} satisfies Record<SupportedLocale, Locale>;

// Type-level checks (these lines compile only if inference is precise):

// 1. `locales.fr` exists because "fr" is a known key.
//    `locales.xx` would be a compile error — no string indexing.
const greeting: string = locales.fr.greeting;

// 2. The keys are a closed set: Object.keys works, but indexing with an
//    arbitrary string would be rejected by the compiler.
const allCodes: readonly SupportedLocale[] = ["en", "de", "fr"];
for (const key of allCodes) {
  // `key` is "en" | "de" | "fr", and locales[key] is type-safe.
  void locales[key].greeting;
}

// 3. Membership test against the SUPPORTED const tuple.
function isSupported(code: string): code is SupportedLocale {
  return (SUPPORTED as readonly string[]).includes(code);
}

console.log(`greeting: ${locales.en.greeting}`);
console.log(`available locales: ${SUPPORTED.join(" ")}`);
console.log(`fr is a known locale: ${isSupported("fr")}`);
