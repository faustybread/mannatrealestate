/**
 * Tailwind config for the luxury real-estate site.
 *
 * Design language: ultra-premium glassmorphism on a deep midnight base,
 * with warm platinum/champagne accents for typographic contrast.
 */

module.exports = {
    content: [
        /* Templates within theme app (theme/templates), e.g. base.html. */
        '../templates/**/*.html',

        /* Project-wide templates directory (BASE_DIR/templates). */
        '../../templates/**/*.html',

        /* Templates in other Django apps (BASE_DIR/<app>/templates). */
        '../../**/templates/**/*.html',
    ],
    theme: {
        extend: {
            colors: {
                /* Deep midnight base — used for body background and darkest surfaces. */
                midnight: {
                    50:  '#e6ebf4',
                    100: '#c2ccdd',
                    200: '#8994b3',
                    300: '#525f83',
                    400: '#2b3557',
                    500: '#1a2340',
                    600: '#131a31',
                    700: '#0d1223',
                    800: '#080b18',
                    900: '#04060f',
                    950: '#02030a',
                },
                /* Champagne / warm platinum — headline accent + CTAs. */
                champagne: {
                    50:  '#fbf7ec',
                    100: '#f5ecd0',
                    200: '#ecdba3',
                    300: '#e0c675',
                    400: '#d4b158',
                    500: '#b8933f',
                    600: '#8f7030',
                    700: '#6a5223',
                    800: '#463617',
                    900: '#241b0b',
                },
            },
            fontFamily: {
                /* Body: Inter — clean, high-contrast sans. */
                sans: ['"Inter"', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
                /* Display: Manrope — modern geometric sans, looks great with wide tracking. */
                display: ['"Manrope"', '"Inter"', 'system-ui', 'sans-serif'],
            },
            letterSpacing: {
                'ultra': '0.28em',
            },
            backdropBlur: {
                xs: '2px',
            },
            boxShadow: {
                /* Ambient inner highlight used on glass panels to fake refraction. */
                'glass':      '0 8px 32px 0 rgba(0, 0, 0, 0.45), inset 0 1px 0 0 rgba(255,255,255,0.06)',
                'glass-lg':   '0 24px 64px -12px rgba(0, 0, 0, 0.6), inset 0 1px 0 0 rgba(255,255,255,0.08)',
                'champagne':  '0 0 0 1px rgba(224,198,117,0.35), 0 12px 40px -8px rgba(212,177,88,0.35)',
            },
            keyframes: {
                'fade-up': {
                    '0%':   { opacity: '0', transform: 'translateY(16px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                'aurora': {
                    '0%,100%': { transform: 'translate3d(0,0,0)' },
                    '50%':     { transform: 'translate3d(-6%, 4%, 0)' },
                },
                'cta-pulse': {
                    '0%,100%': { boxShadow: '0 0 18px rgba(212,177,88,0.18), 0 4px 18px rgba(0,0,0,0.32)' },
                    '50%':     { boxShadow: '0 0 38px rgba(212,177,88,0.48), 0 6px 24px rgba(0,0,0,0.4)' },
                },
            },
            animation: {
                'fade-up':   'fade-up 0.9s cubic-bezier(0.16, 1, 0.3, 1) both',
                'aurora':    'aurora 22s ease-in-out infinite',
                'cta-pulse': 'cta-pulse 2.8s ease-in-out infinite',
            },
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
        /* @tailwindcss/line-clamp is now built into Tailwind v3.3+ core; omitted. */
    ],
}
