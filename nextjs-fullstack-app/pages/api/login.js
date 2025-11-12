// nextjs-fullstack-app/pages/api/login.js

export default function handler(req, res) {
  if (req.method === 'POST') {
    const { email, password } = req.body;

    // 간단한 로그인 인증 로직 (실제 DB 연동은 이 위치에서 진행됩니다.)
    if (email === "test@example.com" && password === "password123") {
      // 인증 성공 시 200 응답과 가짜 토큰 반환
      res.status(200).json({ 
          success: true, 
          message: '로그인 성공', 
          token: 'fake-jwt-token-for-user' 
      });
    } else {
      // 인증 실패 시 401 Unauthorized 응답
      res.status(401).json({ 
          success: false, 
          message: '이메일 또는 비밀번호가 올바르지 않습니다.' 
      });
    }
  } else {
    // POST 메서드 외 요청은 차단 (405 Method Not Allowed)
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}