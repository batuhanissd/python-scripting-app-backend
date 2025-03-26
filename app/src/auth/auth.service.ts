/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-unsafe-assignment */
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { LoginDto } from './dto/login.dto';
import { JwtService } from '@nestjs/jwt';

@Injectable()
export class AuthService {
  constructor(private jwtService: JwtService) {}

  async login(
    loginDto: LoginDto,
  ): Promise<{ accessToken: string; PTSAuth: string }> {
    try {
      const { username, password } = loginDto;
      const response = await fetch(
        'https://pts.mangobulut.com/apib/auth/login',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        },
      );

      if (!response.ok) {
        const data = await response.json();
        throw new UnauthorizedException(data);
      }

      const data = await response.json();
      const PTSAuth: string = data.accessToken;

      const payload: string = this.jwtService.decode(PTSAuth);
      const accessToken: string = this.jwtService.sign(payload);

      return { accessToken, PTSAuth };
    } catch (error) {
      console.error('Error during login:', error);
      throw error;
    }
  }
}
