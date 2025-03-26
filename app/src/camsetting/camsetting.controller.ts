/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-unsafe-assignment */
import {
  Controller,
  Post,
  BadRequestException,
  Headers,
  Body,
  UseGuards,
} from '@nestjs/common';
import { CamsettingService } from './camsetting.service';
import { TokenDto } from './dto/token.dto';
import { PythonScriptService } from './pythonscriptservice.service';
import { JwtAuthGuard } from 'src/auth/jwt-auth.guard';

@Controller('camsetting')
export class CamsettingController {
  constructor(
    private camsettingService: CamsettingService,
    private pythonScService: PythonScriptService,
  ) {}

  //Authorization header'ı doğrular ve token'ı döner.
  private extractToken(authHeader: string): TokenDto {
    if (!authHeader?.startsWith('Bearer ')) {
      throw new BadRequestException('Invalid or missing Authorization header');
    }

    const token = authHeader.slice(7).trim();
    if (!token) {
      throw new BadRequestException('Token is missing');
    }

    return { token };
  }

  @Post('/getcamera')
  async getCamera(@Headers('authorization') authHeader: string): Promise<any> {
    const tokenDto = this.extractToken(authHeader);
    return await this.camsettingService.getCamera(tokenDto);
  }

  @Post('/getnode')
  async getNode(@Headers('authorization') authHeader: string): Promise<any> {
    const tokenDto = this.extractToken(authHeader);
    return await this.camsettingService.getNode(tokenDto);
  }

  @Post('/getsubnode')
  async getSubnode(@Headers('authorization') authHeader: string): Promise<any> {
    const tokenDto = this.extractToken(authHeader);
    return await this.camsettingService.getSubNode(tokenDto);
  }

  @Post('/runconfig')
  @UseGuards(JwtAuthGuard)
  async runConfig(
    @Body()
    body: {
      processType: string;
      selectedCamera: { biosid: string; ipAddress: string }[];
    },
    @Headers('authorization') authHeader: string,
  ): Promise<any> {
    this.extractToken(authHeader); // eger token yoksa ya da hataliysa hata firlatir.
    const selectedCamera = body.selectedCamera;
    const processType = body.processType;
    console.log(selectedCamera);

    try {
      const result = await this.pythonScService.runPythonScript(
        processType,
        selectedCamera,
      );
      return { success: true, result };
    } catch (error) {
      console.error('Python script error:', error);
      return { success: false, message: error.message };
    }
  }

  @Post('/getlogs')
  @UseGuards(JwtAuthGuard)
  async getLogs(@Headers('authorization') authHeader: string): Promise<any> {
    const tokenDto = this.extractToken(authHeader);
    if (tokenDto) {
      return await this.camsettingService.getLogs();
    }
  }
}
