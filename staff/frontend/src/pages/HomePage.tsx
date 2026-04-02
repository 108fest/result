import { useEffect, useState } from "react";

import { getNews, type NewsItem } from "../lib/api";

export function HomePage() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getNews()
      .then((items) => setNews(items))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section>
      <h1>Corporate News</h1>
      {loading && <p>Loading...</p>}
      <div className="grid">
        {news.map((item) => (
          <article key={item.id} className="card news-card">
            <h3>{item.title}</h3>
            <p>{item.summary}</p>
            <small>{new Date(item.created_at).toLocaleString()}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
