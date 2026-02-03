/**
 * PAC timbrado interface
 */

export interface TimbradoResult {
  xmlTimbrado: string;
  uuid?: string;
  fechaTimbrado?: string;
}

export interface PacTimbrador {
  timbrar(xml: string): Promise<TimbradoResult>;
}

export class PacTimbradorMock implements PacTimbrador {
  async timbrar(xml: string): Promise<TimbradoResult> {
    return {
      xmlTimbrado: xml,
    };
  }
}
