/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-unsafe-assignment */
import { Injectable, UnauthorizedException } from '@nestjs/common';
import { LoginDto } from './dto/login.dto';

@Injectable()
export class AuthService {
  async login(loginDto: LoginDto): Promise<{ accessToken: string }> {
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
      const accessToken: string = data.accessToken;
      return { accessToken };
    } catch (error) {
      console.error('Error during login:', error);
      throw error;
    }
  }
}
