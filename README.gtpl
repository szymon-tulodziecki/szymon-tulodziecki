<div align="center">
  <table>
    <tr>
      <td align="left" valign="center">
        <a href="https://git.io/awesome-stats-card">
          <img src="https://awesome-github-stats.azurewebsites.net/user-stats/szymon-tulodziecki?cardType=github&theme=gotham&fontFamily=Merriweather%20Sans&preferLogin=false" alt="My Awesome Stats" />
        </a>
      </td>
      <td align="center" valign="center">
        <img src="https://raw.githubusercontent.com/szymon-tulodziecki/szymon-tulodziecki/output/github-contribution-grid-snake.svg" alt="GitHub Snake" width="350" />
      </td>
    </tr>
  </table>
</div>

---

### Recent Activity
{{range recentContributions 5}}
- **[{{.Repo.Name}}]({{.Repo.URL}})** – {{.Message}} ({{humanize .OccurredAt}})
{{end}}

### Projects
{{range recentRepos 5}}
- [{{.Name}}]({{.URL}}) – {{.Description}}
{{end}}

<p align="right"><i>Last update: {{currentDate}}</i></p>