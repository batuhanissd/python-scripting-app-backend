// import { Injectable, UnauthorizedException } from '@nestjs/common';
// import { PassportStrategy } from '@nestjs/passport';
// import { ExtractJwt, Strategy } from 'passport-jwt';
// import { JwtPayload } from './jwt-payload.interface';

// @Injectable()
// export class JWTStrategy extends PassportStrategy(Strategy, 'jwt') {
//   constructor() {
//     super({
//       secretOrKey: 'topsecret',
//       jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
//     });
//   }

//   async validate(payload: JwtPayload): Promise<string> {
//     if (!user) throw new UnauthorizedException();
//     return user;
//   }
// }
