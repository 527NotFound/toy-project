// nextjs-fullstack-app/pages/login.js

import React, { useState } from 'react';
import { Mail, Lock } from 'lucide-react'; 
// CSS 파일을 import 합니다.
import '../styles/LoginScreen.css'; 

// 개별 입력 필드 컴포넌트
const CustomInput = ({ type, placeholder, icon: Icon, value, onChange }) => (
  <div className="input-group">
    <Icon className="input-icon" size={20} />
    <input
      type={type}
      placeholder={placeholder}
      className="input-field"
      value={value}
      onChange={onChange}
    />
  </div>
);

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    
    // 통합 Next.js 프로젝트에서는 상대 경로로 API를 호출합니다.
    const apiUrl = '/api/login'; 

    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (response.ok) {
            setMessage(`로그인 성공! 환영합니다.`);
            // 성공 후 페이지 이동 또는 토큰 저장 로직
        } else {
            setMessage(`로그인 실패: ${data.message || '알 수 없는 오류'}`);
        }
    } catch (error) {
        console.error('API 호출 중 오류 발생:', error);
        setMessage('서버와 통신하는 데 실패했습니다.');
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="login-screen-wrapper">
      <form className="login-form" onSubmit={handleSubmit}>
        
        {/* 안내 메시지 */}
        {message && <p className={`status-message ${message.includes('성공') ? 'success' : 'error'}`}>{message}</p>}

        {/* 이메일 입력 필드 */}
        <CustomInput
          type="email"
          placeholder="Email ID"
          icon={Mail}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        {/* 비밀번호 입력 필드 */}
        <CustomInput
          type="password"
          placeholder="Password"
          icon={Lock}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {/* 로그인 버튼 */}
        <button type="submit" className="sign-in-button" disabled={loading}>
          {loading ? '로그인 중...' : 'Sign In'}
        </button>

        {/* 추가 옵션 및 링크 */}
        <div className="options-container">
          <label className="remember-me-checkbox">
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
            />
            Remember me
          </label>
          
          <a href="/forgot-password" className="forgot-password-link">
            Forgot Password?
          </a>
        </div>
      </form>
    </div>
  );
}