// @ts-check
// `@ts-check`注释让VS Code等编辑器对此文件进行类型检查
// 详见: https://www.typescriptlang.org/tsconfig#imports-not-used-as-values

const lightCodeTheme = require('prism-react-renderer').themes.github;
const darkCodeTheme = require('prism-react-renderer').themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'AI Tech Blog',
  tagline: 'AI Technology Insights in Multiple Languages',
  favicon: 'img/favicon.ico',

  // 生产环境URL
  url: 'http://101.42.11.124',
  baseUrl: '/',

  // GitHub Pages配置
  organizationName: 'ai-tech-blog',
  projectName: 'ai-tech-blog',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // i18n 多语言配置
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'zh', 'ja'],
    localeConfigs: {
      en: {
        label: 'English',
        direction: 'ltr',
      },
      zh: {
        label: '中文',
        direction: 'ltr',
      },
      ja: {
        label: '日本語',
        direction: 'ltr',
      },
    },
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: false, // 仅使用博客功能
        blog: {
          routeBasePath: '/', // 博客作为首页
          blogTitle: 'AI Tech Blog',
          blogDescription: 'Professional AI technology insights and analysis',
          postsPerPage: 10,
          showReadingTime: true,
          readingTime: ({ content, defaultReadingTime }) =>
            defaultReadingTime({ content, options: { wordsPerMinute: 200 } }),
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // 社交卡片图片
      image: 'img/social-card.png',
      navbar: {
        title: 'AI Tech Blog',
        logo: {
          alt: 'AI Tech Blog Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'localeDropdown',
            position: 'right',
          },
          {
            href: 'https://github.com/your-org/ai-tech-blog',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        copyright: `Copyright © ${new Date().getFullYear()} AI Tech Blog. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
    }),
};

module.exports = config;
