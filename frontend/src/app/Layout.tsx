import { useCallback, useEffect, useRef, useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import ConnectionStatus from './ConnectionStatus';

const NAV_ITEMS = [
  { to: '/', label: '记录', end: true },
  { to: '/materials', label: '素材', end: false },
  { to: '/sources', label: '来源', end: false },
  { to: '/propositions', label: '观点', end: false },
];

export default function Layout() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const location = useLocation();
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const sidebarRef = useRef<HTMLElement>(null);

  // 路由变化时收起抽屉，焦点还给菜单按钮
  useEffect(() => {
    setDrawerOpen(false);
  }, [location.pathname, location.search]);

  useEffect(() => {
    if (!drawerOpen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setDrawerOpen(false);
        menuButtonRef.current?.focus();
      }
    };
    document.addEventListener('keydown', onKeyDown);
    const firstLink = sidebarRef.current?.querySelector<HTMLElement>('a');
    firstLink?.focus();
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [drawerOpen]);

  const closeDrawer = useCallback(() => {
    setDrawerOpen(false);
    menuButtonRef.current?.focus();
  }, []);

  return (
    <div className="app-shell">
      <div className="mobile-topbar">
        <button
          ref={menuButtonRef}
          type="button"
          className="menu-button"
          aria-label="打开导航菜单"
          aria-expanded={drawerOpen}
          onClick={() => setDrawerOpen(true)}
        >
          ☰
        </button>
        <span className="brand" style={{ margin: 0 }}>
          抵达 Arrive
        </span>
      </div>

      {drawerOpen && (
        <button
          type="button"
          className="drawer-backdrop"
          aria-label="关闭导航菜单"
          onClick={closeDrawer}
        />
      )}

      <nav
        ref={sidebarRef}
        className={drawerOpen ? 'sidebar sidebar--open' : 'sidebar'}
        aria-label="主导航"
      >
        <p className="brand">
          抵达 Arrive
          <small>把思考忠实放下来</small>
        </p>
        <div className="nav-list">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className="nav-link"
            >
              {item.label}
            </NavLink>
          ))}
        </div>
        <div className="sidebar-footer">
          <ConnectionStatus />
          <p>
            数据保存在本机数据根。当前服务无认证，仅限本地或受控环境使用。
          </p>
        </div>
      </nav>

      <div className="main-area">
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
