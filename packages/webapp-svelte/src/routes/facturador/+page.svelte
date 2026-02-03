<script lang="ts">
  import { buildUnsignedCfdiXml } from 'catalogmx/cfdi';
  import { validateXmlWithXsd } from '$lib/cfdi/xsd-validator';

  let emisorRfc = 'AAA010101AAA';
  let emisorNombre = 'EMISOR DEMO SA DE CV';
  let emisorRegimen = '601';

  let receptorRfc = 'XAXX010101000';
  let receptorNombre = 'PUBLICO EN GENERAL';
  let receptorUso = 'G03';
  let receptorRegimen = '616';
  let receptorCp = '64000';

  let claveProdServ = '01010101';
  let cantidad = '1';
  let claveUnidad = 'H87';
  let descripcion = 'Servicio de ejemplo';
  let valorUnitario = '100.00';
  let importe = '100.00';

  let moneda = 'MXN';
  let tipoDeComprobante = 'I';
  let lugarExpedicion = '64000';
  let subTotal = '100.00';
  let total = '100.00';

  let xml = '';
  let cadena = '';
  let xsdValid: null | boolean = null;
  let xsdErrors: string[] = [];

  function generar() {
    xml = buildUnsignedCfdiXml({
      moneda,
      tipoDeComprobante,
      lugarExpedicion,
      subTotal,
      total,
      emisor: {
        rfc: emisorRfc,
        nombre: emisorNombre,
        regimenFiscal: emisorRegimen
      },
      receptor: {
        rfc: receptorRfc,
        nombre: receptorNombre,
        usoCfdi: receptorUso,
        regimenFiscalReceptor: receptorRegimen,
        domicilioFiscalReceptor: receptorCp
      },
      conceptos: [
        {
          claveProdServ,
          cantidad,
          claveUnidad,
          descripcion,
          valorUnitario,
          importe
        }
      ]
    });
    cadena = '';
    xsdValid = null;
    xsdErrors = [];
  }

  async function generarCadena() {
    if (!xml) return;
    const xsltUrl = '/data/sat/xsd/resources/www.sat.gob.mx/sitio_internet/cfd/4/cadenaoriginal_4_0/cadenaoriginal_4_0.xslt';
    const response = await fetch(xsltUrl);
    if (!response.ok) {
      throw new Error(`No se pudo cargar XSLT: ${response.statusText}`);
    }
    const xsltText = await response.text();
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xml, 'application/xml');
    const xsltDoc = parser.parseFromString(xsltText, 'application/xml');
    const processor = new XSLTProcessor();
    processor.importStylesheet(xsltDoc);
    const result = processor.transformToDocument(xmlDoc);
    cadena = result.documentElement?.textContent?.trim() ?? '';
  }

  async function validarXsd() {
    if (!xml) return;
    const xsdUrl = '/data/sat/xsd/resources/www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd';
    const response = await fetch(xsdUrl);
    if (!response.ok) {
      throw new Error(`No se pudo cargar XSD: ${response.statusText}`);
    }
    const xsdText = await response.text();
    const result = await validateXmlWithXsd(xml, xsdText);
    xsdValid = result.valid;
    xsdErrors = result.errors;
  }

  generar();
</script>

<svelte:head>
  <title>Facturador CFDI - catalogmx</title>
</svelte:head>

<div class="page">
  <div class="header">
    <h1>Facturador CFDI (XML para sellar)</h1>
    <p>Genera un XML CFDI 4.0 sin sello para pruebas.</p>
  </div>

  <div class="grid">
    <section class="card">
      <h2>Emisor</h2>
      <label>RFC<input bind:value={emisorRfc} /></label>
      <label>Nombre<input bind:value={emisorNombre} /></label>
      <label>Régimen<input bind:value={emisorRegimen} /></label>

      <h2>Receptor</h2>
      <label>RFC<input bind:value={receptorRfc} /></label>
      <label>Nombre<input bind:value={receptorNombre} /></label>
      <label>Uso CFDI<input bind:value={receptorUso} /></label>
      <label>Régimen<input bind:value={receptorRegimen} /></label>
      <label>CP<input bind:value={receptorCp} /></label>

      <h2>Concepto</h2>
      <label>Clave Prod/Serv<input bind:value={claveProdServ} /></label>
      <label>Cantidad<input bind:value={cantidad} /></label>
      <label>Clave Unidad<input bind:value={claveUnidad} /></label>
      <label>Descripción<input bind:value={descripcion} /></label>
      <label>V. Unitario<input bind:value={valorUnitario} /></label>
      <label>Importe<input bind:value={importe} /></label>

      <h2>Comprobante</h2>
      <label>Moneda<input bind:value={moneda} /></label>
      <label>Tipo<input bind:value={tipoDeComprobante} /></label>
      <label>Lugar Expedición<input bind:value={lugarExpedicion} /></label>
      <label>Subtotal<input bind:value={subTotal} /></label>
      <label>Total<input bind:value={total} /></label>

      <button on:click={generar}>Generar XML</button>
      <button on:click={generarCadena} style="margin-top:8px;background:#1d4ed8;">Generar cadena original</button>
      <button on:click={validarXsd} style="margin-top:8px;background:#0f766e;">Validar XSD (WASM)</button>
    </section>

    <section class="card">
      <h2>XML (para sellar)</h2>
      <textarea readonly rows="30" bind:value={xml}></textarea>
      <h2 style="margin-top:16px;">Cadena original</h2>
      <textarea readonly rows="6" bind:value={cadena}></textarea>
      <h2 style="margin-top:16px;">Validación XSD</h2>
      {#if xsdValid === null}
        <div class="status">Sin validar</div>
      {:else if xsdValid}
        <div class="status ok">XML válido contra XSD</div>
      {:else}
        <div class="status error">XML inválido</div>
        <ul class="errors">
          {#each xsdErrors as err}
            <li>{err}</li>
          {/each}
        </ul>
      {/if}
    </section>
  </div>
</div>

<style>
  .page {
    padding: 32px;
  }
  .header {
    margin-bottom: 20px;
  }
  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
  .card {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
    background: #fff;
  }
  label {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 10px;
    font-size: 13px;
  }
  input {
    padding: 8px 10px;
    border: 1px solid #cbd5f5;
    border-radius: 8px;
  }
  textarea {
    width: 100%;
    border: 1px solid #cbd5f5;
    border-radius: 8px;
    padding: 10px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-size: 12px;
  }
  button {
    padding: 10px 14px;
    border: none;
    border-radius: 10px;
    background: #0f766e;
    color: #fff;
    cursor: pointer;
  }
  .status {
    margin-top: 8px;
    font-size: 13px;
    color: #64748b;
  }
  .status.ok {
    color: #16a34a;
    font-weight: 600;
  }
  .status.error {
    color: #dc2626;
    font-weight: 600;
  }
  .errors {
    margin: 8px 0 0;
    padding-left: 16px;
    font-size: 12px;
    color: #b91c1c;
  }
  @media (max-width: 900px) {
    .grid {
      grid-template-columns: 1fr;
    }
  }
</style>
