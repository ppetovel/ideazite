// /analytics/ga-init.js
(function(){
  // Cargar librería de Google Analytics 4
  var s = document.createElement("script");
  s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=G-WBBBSGK7YX";
  document.head.appendChild(s);

  // DataLayer y gtag
  window.dataLayer = window.dataLayer || [];
  function gtag(){ dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  // Inicializar GA4
  gtag('js', new Date());

  // Configuración con page_path real
  gtag('config', 'G-WBBBSGK7YX', {
    send_page_view: true,
    transport_type: 'beacon',
    page_path: window.location.pathname // asegura que GA4 registre la URL de cada campaña
  });
})();
