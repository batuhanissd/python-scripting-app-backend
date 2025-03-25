import { Body, Controller, Post } from '@nestjs/common';
import { LoginDto } from './dto/login.dto';
import { AuthService } from './auth.service';

@Controller('auth')
export class AuthController {
  constructor(private authService: AuthService) { }
  @Post('/userlogin')
  async login(@Body() LoginDto: LoginDto): Promise<{ accessToken: string }> {
    return await this.authService.login(LoginDto);
  }
}
