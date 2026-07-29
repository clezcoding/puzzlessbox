import type { Config } from 'tailwindcss';

export default {
  theme: {
    extend: {
      colors: {
        bg: 'var(--color-bg)',
        'bg-wash': 'var(--color-bg-wash)',
        surface: 'var(--color-surface)',
        'surface-soft': 'var(--color-surface-soft)',
        border: 'var(--color-border)',
        'border-strong': 'var(--color-border-strong)',
        text: 'var(--color-text)',
        'text-muted': 'var(--color-text-muted)',
        primary: 'var(--color-primary)',
        'primary-hover': 'var(--color-primary-hover)',
        brand: 'var(--color-brand)',
        'brand-soft': 'var(--color-brand-soft)',
        accent: 'var(--color-accent)',
        'accent-soft': 'var(--color-accent-soft)',
        cardboard: 'var(--color-cardboard)',
        info: 'var(--color-info)',
        'info-soft': 'var(--color-info-soft)',
        destructive: 'var(--color-destructive)',
        'ink-bar': 'var(--color-ink-bar)',
        inbox: {
          bg: 'var(--color-inbox-bg)',
          accent: 'var(--color-inbox-accent)',
        },
        notes: {
          bg: 'var(--color-notes-bg)',
          accent: 'var(--color-notes-accent)',
        },
        links: {
          bg: 'var(--color-links-bg)',
          accent: 'var(--color-links-accent)',
        },
        tasks: {
          bg: 'var(--color-tasks-bg)',
          accent: 'var(--color-tasks-accent)',
        },
        termine: {
          bg: 'var(--color-termine-bg)',
          accent: 'var(--color-termine-accent)',
        },
      },
      fontFamily: {
        display: ['var(--font-display)', 'serif'],
        serif: ['var(--font-serif)', 'serif'],
        sans: ['var(--font-sans)', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
      fontSize: {
        body: ['var(--text-body)', { lineHeight: 'var(--text-body-leading)', fontWeight: 'var(--text-body-weight)' }],
        label: ['var(--text-label)', { lineHeight: 'var(--text-label-leading)', fontWeight: 'var(--text-label-weight)' }],
        heading: ['var(--text-heading)', { lineHeight: 'var(--text-heading-leading)', fontWeight: 'var(--text-heading-weight)' }],
        display: ['var(--text-display)', { lineHeight: 'var(--text-display-leading)', fontWeight: 'var(--text-display-weight)' }],
      },
      spacing: {
        xs: 'var(--spacing-xs)',
        sm: 'var(--spacing-sm)',
        md: 'var(--spacing-md)',
        lg: 'var(--spacing-lg)',
        xl: 'var(--spacing-xl)',
        '2xl': 'var(--spacing-2xl)',
        '3xl': 'var(--spacing-3xl)',
      },
    },
  },
} satisfies Config;
