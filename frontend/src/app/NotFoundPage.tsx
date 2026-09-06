import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div>
      <h1>页面不存在</h1>
      <p className="muted">这个地址没有对应的页面。</p>
      <p>
        <Link to="/">回到记录页</Link>
      </p>
    </div>
  );
}
