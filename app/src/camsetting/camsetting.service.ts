/* eslint-disable @typescript-eslint/no-unsafe-assignment */
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { TokenDto } from './dto/token.dto';
import { PythonScriptService } from './pythonscriptservice.service';

@Injectable()
export class CamsettingService {
  constructor(private pythonService: PythonScriptService) {}

  async getCamera(tokendto: TokenDto): Promise<any> {
    try {
      const token = tokendto.token;
      const response = await fetch(
        'https://pts.mangobulut.com/apib/camera/record-capture-time?order=ASC',
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        },
      );
      if (!response.ok) throw new UnauthorizedException();
      const data = await response.json();
      //const biosIds = data.map((item) => item.biosId);
      return this.pythonService.runPythonScript(data, 'Cameras');
    } catch (error) {
      console.error(
        'Error occurred while fetching data or running Python script:',
        error,
      );
      throw error;
    }
  }

  async getNode(tokenDto: TokenDto): Promise<any> {
    try {
      const token = tokenDto.token;
      const response = await fetch('https://pts.mangobulut.com/apib/node', {
        method: 'Get',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new UnauthorizedException();

      const data = await response.json();
      return this.pythonService.runPythonScript(data, 'Nodes');
    } catch (error) {
      console.error(
        'Error occurred while fetching data or running Python script:',
      );
      throw error;
    }
  }

  async getSubNode(tokendto: TokenDto): Promise<any> {
    try {
      const token = tokendto.token;
      const response = await fetch('https://pts.mangobulut.com/apib/sub-node', {
        method: 'Get',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new UnauthorizedException();

      const data = await response.json();
      return this.pythonService.runPythonScript(data, 'Sub-Nodes');
    } catch (error) {
      console.error(
        'Error occurred while fetching data or running Python script:',
      );
      throw error;
    }
  }
}
