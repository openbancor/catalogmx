import { Helmet } from 'react-helmet-async';

interface SEOHeadProps {
  title?: string;
  description?: string;
  keywords?: string;
  image?: string;
  url?: string;
  type?: 'website' | 'article';
}

export default function SEOHead({
  title = 'catalogmx - Validación y Catálogos para México',
  description = 'Librería de validación y catálogos oficiales para México. Incluye RFC, CURP, CLABE, códigos postales, bancos, UDI, tipo de cambio y más.',
  keywords = 'México, validación, catálogos, RFC, CURP, CLABE, NSS, SAT, INEGI, Banxico, códigos postales, bancos, UDI, tipo de cambio, inflación',
  image = '/og-image.png',
  url = typeof window !== 'undefined' ? window.location.href : '',
  type = 'website',
}: SEOHeadProps) {
  const fullTitle = title === 'catalogmx - Validación y Catálogos para México'
    ? title
    : `${title} | catalogmx`;

  const baseUrl = import.meta.env.BASE_URL || '/';
  const fullImage = image.startsWith('http') ? image : `${baseUrl}${image}`;

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={type} />
      <meta property="og:url" content={url} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={fullImage} />
      <meta property="og:site_name" content="catalogmx" />

      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:url" content={url} />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={fullImage} />

      {/* Additional Meta Tags */}
      <meta name="robots" content="index, follow" />
      <meta name="language" content="Spanish" />
      <meta name="author" content="OpenBancor" />
      <link rel="canonical" href={url} />
    </Helmet>
  );
}
