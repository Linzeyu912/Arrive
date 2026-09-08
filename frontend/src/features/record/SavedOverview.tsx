import { Link } from 'react-router-dom';
import { listMaterials, listSources } from '../../api/endpoints';
import { useLoad } from '../../lib/useLoad';
import { ErrorView, LoadingView } from '../../components/StatusView';

const load = async () => {
  const [materials, sources] = await Promise.all([listMaterials(), listSources()]);
  return { materials, sources };
};

export default function SavedOverview() {
  const { state, reload } = useLoad(load);
  return <section aria-label="本地已保存记录" style={{ marginTop: 32 }}>
    <h2>本地已保存</h2>
    {state.status === 'loading' && <LoadingView />}
    {state.status === 'error' && <ErrorView error={state.error} onRetry={reload} />}
    {state.status === 'success' && <>
      <p><Link to="/materials">素材 {state.data.materials.length} 条</Link> · <Link to="/sources">来源 {state.data.sources.length} 条</Link> · <Link to="/local-records">旧文件档案</Link></p>
      {state.data.sources.slice(-3).reverse().map(source => <p key={source.id}><Link to={`/sources/${source.id}`}>{source.title}</Link></p>)}
      <button type="button" className="button" onClick={reload}>刷新已保存记录</button>
    </>}
  </section>;
}
