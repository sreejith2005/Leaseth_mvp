/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: '#faf8f5',
        ink: '#1a1a18',
        sage: '#7c9a82',
        terracotta: '#c4704f',
        sand: '#d4c5b0',
        primary: {
          50: '#f0f5f1',
          100: '#dce8de',
          200: '#b9d1bd',
          300: '#96ba9c',
          400: '#7c9a82',
          500: '#5c7a62',
          600: '#4a624f',
          700: '#3b4e3f',
          800: '#2d3b30',
          900: '#1f2821',
        },
        risk: {
          low: '#7c9a82',
          medium: '#d4a574',
          high: '#c4704f',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['DM Serif Display', 'Georgia', 'serif'],
      },
      fontSize: {
        '2xs': '0.625rem',
      },
      letterSpacing: {
        tight: '-0.02em',
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out forwards',
        'slide-up': 'slideUp 0.3s ease-out',
        'blob-morph': 'blobMorph 8s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          from: { opacity: '0', transform: 'translateY(10px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        blobMorph: {
          '0%, 100%': { borderRadius: '60% 40% 30% 70% / 60% 30% 70% 40%' },
          '50%': { borderRadius: '30% 60% 70% 40% / 50% 60% 30% 60%' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      boxShadow: {
        'soft': '0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03)',
        'soft-lg': '0 2px 8px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.05)',
      }
    },
  },
  plugins: [],
}
