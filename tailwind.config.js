/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './medlog/core/templates/**/*.html',
    './node_modules/flowbite/**/*.js'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {"50":"#ecfdf5","100":"#d1fae5","200":"#a7f3d0","300":"#6ee7b7","400":"#34d399","500":"#10b981","600":"#059669","700":"#047857","800":"#065f46","900":"#064e3b","950":"#022c22"},
        "custom-gray": {"100":"#5e5e5e","200":"#444343","300":"#3E3D3D","400":"#2F3333"}
      },
      animation: {
        modalf: "modalf 0.1s ease-in-out",
      },
      keyframes: {
          modalf: {
              "0%": { transform: "scale(0)" },
              "100%": { transform: "scale(1)" },
          },
      },
    },
  },
  plugins: [
    require('flowbite/plugin')
  ]
}

